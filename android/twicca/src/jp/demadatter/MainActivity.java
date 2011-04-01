/*-*- coding:utf-8; mode:java-mode -*-*/
/*
	デマだったー
		チームこれから
*/
package jp.demadatter;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.net.Uri;
import android.content.Intent;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.TextView;
import android.preference.PreferenceManager;
import android.text.format.DateFormat;

import java.util.Date;
import java.util.HashMap;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

public class MainActivity
	extends Activity
	implements View.OnClickListener
{
	/** twiccaツイート表示プラグインExtra:スクリーンネーム */
	private static final String EXTRA_SCREEN_NAME = "user_screen_name";
	/** twiccaツイート表示プラグインExtra:ユーザー名 */
	private static final String EXTRA_USER_NAME = "user_name";
	/** twiccaツイート表示プラグインExtra:ツイートID */
	private static final String EXTRA_TWEET_ID = "id";
	/** twiccaツイート表示プラグインExtra:ツイート日時 */
	private static final String EXTRA_CREATED = "created_at";

	/** ユーザトークン設定キー */
	private static final String PREF_TOKEN = "token";
	/** レポート済みレポート設定キー */
	private static final String PREF_REPORT_TWEET = "reportid";
	/** レポート済みレポート区切り文字 */
	private static final String REPORT_DELIMITER = ",";
	/** レポート済みレポート保存数 */
	private static final int SAVE_REPORT_COUNT = 10;

	/** ハンドラ */
	private Handler mHandler = new MainHandler();
	/** メッセージ:デマ件数取得 */
	private static final int MSG_GETCOUNT = 1;
	/** メッセージ:レポート */
	private static final int MSG_REPORTED = 2;

	/** プログレスダイアログ */
	private ProgressDialog mProgress;

	/** ユーザトークン(デマだったーのトークンキー) */
	private String mToken;
	/** ツイート本文 */
	private String mTweet;
	/** スクリーン名 */
	private String mScreenName;
	/** ユーザー名 */
	private String mUserName;
	/** ツイートID */
	private String mTweetID;
	/** ツイート日時 */
	private String mCreatedAt;

	/**
	 * Create時処理
	 * @param	savedInstanceState
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		requestWindowFeature(android.view.Window.FEATURE_NO_TITLE);
		setContentView(R.layout.main);

		// ユーザートークン ※Twitter APIのトークンではない
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
		mToken = pref.getString(PREF_TOKEN, "");

		// ツイート情報取得
		Intent intent = getIntent();
		mTweet = intent.getStringExtra(Intent.EXTRA_TEXT);
		mScreenName = intent.getStringExtra(EXTRA_SCREEN_NAME);
		mUserName = intent.getStringExtra(EXTRA_USER_NAME);
		mTweetID = intent.getStringExtra(EXTRA_TWEET_ID);
		mCreatedAt = intent.getStringExtra(EXTRA_CREATED);
		Date date = new Date(Long.parseLong(mCreatedAt));
		if ((mCreatedAt != null) && (mCreatedAt.length() > 3)) {
			// ミリ秒 → 秒
			mCreatedAt = mCreatedAt.substring(0, mCreatedAt.length() - 3);
		}

		// ツイート情報表示
		setViewText(R.id.main_name_text, "@" + mScreenName);
		setViewText(R.id.main_user_text, mUserName);
		setViewText(R.id.main_tweet_text, mTweet);
		setViewText(R.id.main_date_text, 
					DateFormat.getDateFormat(this).format(date) + " " +
					DateFormat.getTimeFormat(this).format(date));

		// ボタン準備
		findViewById(R.id.main_ranking_btn).setOnClickListener(this);
		findViewById(R.id.main_dt_btn).setOnClickListener(this);
		findViewById(R.id.main_report_btn).setOnClickListener(this);

		// デマ件数確認
		getDemaCount();
	}

	/**
	 * クリックイベント処理
	 * @param	view	イベントが発生したView
	 */
	public void onClick(View view) {
		switch (view.getId()) {
		case R.id.main_ranking_btn:		// ランキング
			onClickRanking();
			break;

		case R.id.main_dt_btn:			// DT
			onClickDT();
			break;

		case R.id.main_report_btn:		// Report
			onClickReport();
			break;
		}
	}

	/**
	 * ランキング
	 */
	private void onClickRanking() {
		// Twicca編集画面へ
		Uri uri = Uri.parse(getResources().getString(R.string.ranking_url));
		Intent intent = new Intent(Intent.ACTION_VIEW, uri);
		startActivity(intent);
	}

	/**
	 * DT
	 */
	private void onClickDT() {
		// メッセージ作成
		String message = String.format(getResources().getString(R.string.dt_format), mScreenName, mTweet);
		// URL構成
		String url = getResources().getString(R.string.tweet_url);
		try {
			url += URLEncoder.encode(message, "UTF-8");
		} catch (java.io.UnsupportedEncodingException e) {
			// エラーしちゃったら、、、しょうがないからそのまま追加?
			url += message;
		}
		// Twicca編集画面へ
		Uri uri = Uri.parse(url);
		Intent intent = new Intent(Intent.ACTION_VIEW, uri);
		startActivity(intent);
	}

	/**
	 * レポート要求
	 */
	private void onClickReport() {
		if (idReportTweet(mTweetID)) {
			// レポート済み
			new AlertDialog.Builder(this)
				.setMessage(R.string.already_report)
				.setPositiveButton(R.string.report_result_ok, new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						dialog.dismiss();
					}
					})
				.show();
			return;
		}

		// プログレス表示
		if (mProgress != null) {
			mProgress.dismiss();
		}
		mProgress = ProgressDialog.show(this, null, getResources().getString(R.string.reporting));

		// 通信リクエスト
		final String url = getResources().getString(R.string.report_url);
		final Message msg = mHandler.obtainMessage(MSG_REPORTED);
		new Thread(new Runnable() {
				@Override
				public void run() {
					try {
						String params = "tweetid=" + URLEncoder.encode(mTweetID, "UTF-8")
							+ "&tweet=" + URLEncoder.encode(mTweet, "UTF-8")
							+ "&screen_name=" + URLEncoder.encode(mScreenName, "UTF-8")
							+ "&created_at=" + URLEncoder.encode(mCreatedAt, "UTF-8");
						if (mUserName != null) {
							params += "&user_name=" + URLEncoder.encode(mUserName, "UTF-8");
						}
						if ((mToken != null) && (mToken.length() > 0)) {
							params += "&token=" + mToken;
						}

						HttpURLConnection http = (HttpURLConnection)new URL(url).openConnection();
						http.setRequestMethod("POST");
						http.setDoOutput(true);
						http.getOutputStream().write(params.getBytes());
						byte data[] = new byte[1024];	// GAEは Content-Length が返せない
						int size = http.getInputStream().read(data);
						http.disconnect();
						msg.obj = new String(data, 0, size);
					} catch (Exception e) {
						android.util.Log.e("debug", "onClickReport():" + e.toString());
						msg.obj = null;	// エラー
					}
					msg.sendToTarget();
				}
			}).start();
	}

	/**
	 * デマ件数取得要求
	 */
	private void getDemaCount() {
		// 通信リクエスト
		String params = "?tweetid=" + mTweetID;
		if ((mToken != null) && (mToken.length() > 0)) {
			params += "&token=" + mToken;
		}
		final String url = getResources().getString(R.string.count_url) + params;
		final Message msg = mHandler.obtainMessage(MSG_GETCOUNT);
		new Thread(new Runnable() {
				@Override
				public void run() {
					try {
						HttpURLConnection http = (HttpURLConnection)new URL(url).openConnection();
						http.setRequestMethod("GET");
						http.connect();
						byte data[] = new byte[1024];	// GAEは Content-Length が返せない
						int size = http.getInputStream().read(data);
						http.disconnect();
						msg.obj = new String(data, 0, size);
					} catch (Exception e) {
						android.util.Log.e("debug", "getDemoCount():" + e.toString());
						msg.obj = null;	// エラー
					}
					msg.sendToTarget();
				}
			}).start();
	}

	/**
	 * デマ件数取得結果
	 * @param	msg	メッセージ
	 */
	private void onMsgGetCount(Message msg) {
		if ((msg.obj == null) || !(msg.obj instanceof String)) {
			// 通信失敗?
			showPopup(R.string.report_failure);
			return;
		}
		HashMap<String,Integer> map = parseResult((String)msg.obj);

		String message;
		int count = map.get(mTweetID);
		if (count > 0) {
			// デマ件数表示
			message = String.format(getResources().getString(R.string.count_format), count);
		} else {
			// レポートされていない
			message = getResources().getString(R.string.no_report);
		}
		setViewText(R.id.main_count_text, message);
		findViewById(R.id.main_counting_text).setVisibility(View.GONE);
	}

	/**
	 * レポート結果
	 * @param	msg	メッセージ
	 */
	private void onMsgReported(Message msg) {
		// プログレス表示を消す
		if (mProgress != null) {
			mProgress.dismiss();
			mProgress = null;
		}

		if ((msg.obj == null) || !(msg.obj instanceof String)) {
			// 通信失敗
			showPopup(R.string.report_failure);
			return;
		}

		int count = parseResult((String)msg.obj).get(mTweetID);
		// 成功したらツイートIDを記録しておく
		saveReportTweet(mTweetID);
		// デマ件数更新
		onMsgGetCount(msg);

		// 結果表示
		showPopup(R.string.report_success);
	}

	/**
	 * 通信応答解析
	 * @param	result	通信結果
	 * @return	通信結果のツイートIDマップ
	 */
	private HashMap<String,Integer> parseResult(String result) {
		String lines[] = result.split("\n");
		HashMap<String,Integer> map = new HashMap<String,Integer>();

		for (int index = 0; index < lines.length; index++) {
			String words[] = lines[index].split("=", 2);
			if (words.length < 2) {
				continue;
			}
			if (words[0].equals("token")) {
				// トークン更新
				mToken = words[1];
				SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
				SharedPreferences.Editor editor = pref.edit();
				editor.putString(PREF_TOKEN, mToken);
				editor.commit();
			} else {
				// ツイートID : 件数 マップ
				map.put(words[0], Integer.parseInt(words[1]));
			}
		}
		return map;
	}

	/**
	 * ツイートをレポート済みか判定
	 * @param	id	ツイートID
	 * @return	レポート済み状態
	 */
	private boolean idReportTweet(String id) {
		// レポート済みツイート走査
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
		String report[] = pref.getString(PREF_REPORT_TWEET, "").split(REPORT_DELIMITER);
		for (int index = 0; index < report.length; index++) {
			if (id.equals(report[index])) {
				// レポート済み
				return true;
			}
		}
		// レポートしてないよ
		return false;
	}

	/**
	 * レポートしたツイートを保存
	 * @param	id	ツイートID
	 */
	private void saveReportTweet(String id) {
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
		String report[] = pref.getString(PREF_REPORT_TWEET, "").split(REPORT_DELIMITER);

		// 新しいレポート済みIDリスト
		String save;
		save = id;
		for (int index = 0, count = 1; (index < report.length) && (count < SAVE_REPORT_COUNT); index++, count++) {
			save += REPORT_DELIMITER + report[index];
		}

		// 保存
		SharedPreferences.Editor editor = pref.edit();
		editor.putString(PREF_REPORT_TWEET, save);
		editor.commit();
	}

	private class MainHandler extends Handler {
		/**
		 * メッセージハンドラ
		 * @param	msg	メッセージ
		 */
		@Override
		public void handleMessage(Message msg) {
			switch (msg.what) {
			case MSG_GETCOUNT:			// デマ件数取得
				onMsgGetCount(msg);
				break;

			case MSG_REPORTED:			// レポート
				onMsgReported(msg);
				break;
			}
		}
	}

	/**
	 * 失敗アラート表示
	 * @param	resid	リソースID
	 */
	private void showPopup(int resid) {
		final AlertDialog dialog = new AlertDialog.Builder(this).setMessage(resid).show();
		mHandler.postDelayed(new Runnable() {
				@Override
				public void run() {
					dialog.dismiss();
				}
			}, 3000/*ms*/);
	}

	/**
	 * ビューのテキスト設定(エラーフリー)
	 * @param	resid	リソースID
	 * @param	text	テキスト
	 */
	private void setViewText(int resid, String text) {
		if (text != null) {
			View view = findViewById(resid);
			if ((view != null) && (view instanceof TextView)) {
				((TextView)view).setText(text);
			}
		}
	}
}
