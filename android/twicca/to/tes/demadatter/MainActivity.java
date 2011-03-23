/*-*- coding:utf-8; mode:java-mode -*-*/
/*
	デマだったー
		チームこれから
*/
package to.tes.demadatter;

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

	/** 通報済みレポート設定キー */
	private static final String PREF_REPORT_TWEET = "reportid";
	/** 通報済みレポート区切り文字 */
	private static final String REPORT_DELIMITER = ",";
	/** 通報済みレポート保存数 */
	private static final int SAVE_REPORT_COUNT = 10;

	/** ハンドラ */
	private Handler mHandler = new MainHandler();
	/** メッセージ:デマ件数取得 */
	private static final int MSG_GETCOUNT = 1;
	/** メッセージ:デマ通報 */
	private static final int MSG_NOTIFYDEMA = 2;

	/** プログレスダイアログ */
	private ProgressDialog mProgress;

	/** ツイート本文 */
	private String mTweet;
	/** スクリーン名 */
	private String mScreenName;
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

		// ツイート情報取得
		Intent intent = getIntent();
		mTweet = intent.getStringExtra(Intent.EXTRA_TEXT);
		mScreenName = intent.getStringExtra(EXTRA_SCREEN_NAME);
		mTweetID = intent.getStringExtra(EXTRA_TWEET_ID);
		mCreatedAt = intent.getStringExtra(EXTRA_CREATED);
		Date date = new Date(Long.parseLong(mCreatedAt));
		if ((mCreatedAt != null) && (mCreatedAt.length() > 3)) {
			// ミリ秒 → 秒
			mCreatedAt = mCreatedAt.substring(0, mCreatedAt.length() - 3);
		}

		// ツイート情報表示
		setViewText(R.id.main_name_text, "@" + mScreenName);
		setViewText(R.id.main_user_text, intent.getStringExtra(EXTRA_USER_NAME));
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
	 * デマ通報要求
	 */
	private void onClickReport() {
		if (idReportTweet(mTweetID)) {
			// 通報済み
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
		final String url = "http://voogie01.sakura.ne.jp/demadatter/api/add.cgi";
		final Message msg = mHandler.obtainMessage(MSG_NOTIFYDEMA);
		//DemaServerConnecter.notifyDema(mTweetID, mTweet, mScreenName, mCreatedAt, msg);

		// !!! for test
		new Thread(new Runnable() {
				@Override
				public void run() {
					try {
						String params = "id=" + URLEncoder.encode(mTweetID, "UTF-8")
							+ "&text=" + URLEncoder.encode(mTweet, "UTF-8")
							+ "&user_screen_name=" + URLEncoder.encode(mScreenName, "UTF-8")
							+ "&created_at=" + URLEncoder.encode(mCreatedAt, "UTF-8");
android.util.Log.d("debug", "send param:" + params);

						HttpURLConnection http = (HttpURLConnection)new URL(url).openConnection();
						http.setRequestMethod("POST");
						http.setDoOutput(true);
						http.getOutputStream().write(params.getBytes());
						byte b[] = new byte[http.getContentLength()];
						http.getInputStream().read(b);
						http.disconnect();
						msg.arg1 = Integer.parseInt(new String(b));
					} catch (Exception e) {
						android.util.Log.e("debug", "onClickReport():" + e.toString());
						msg.arg1 = 0;	// エラー
					}
					msg.sendToTarget();
				}
			}).start();
	}

	/**
	 * デマ件数取得要求x
	 */
	private void getDemaCount() {
		// 通信リクエスト
		final String url = "http://voogie01.sakura.ne.jp/demadatter/api/count.cgi?id=" + mTweetID;
		final Message msg = mHandler.obtainMessage(MSG_GETCOUNT);
		//DemaServerConnectergg.getDemaCount(mTweetID, msg);

		// !!! for test
		new Thread(new Runnable() {
				@Override
				public void run() {
					try {
						HttpURLConnection http = (HttpURLConnection)new URL(url).openConnection();
						http.setRequestMethod("GET");
						http.connect();
						byte b[] = new byte[http.getContentLength()];
						http.getInputStream().read(b);
						http.disconnect();
						msg.arg1 = Integer.parseInt(new String(b));
					} catch (Exception e) {
						android.util.Log.e("debug", "getDemoCount():" + e.toString());
						msg.arg1 = -1;	// エラー
					}
					msg.sendToTarget();
				}
			}).start();
	}

	/**
	 * デマ件数取得結果
	 * @param	count	件数
	 */
	private void onMsgGetCount(int count) {
		String message;
		if (count > 0) {
			// デマ件数表示
			message = String.format(getResources().getString(R.string.count_format), count);
		} else {
			// デマ通報されていない
			message = getResources().getString(R.string.no_report);
		}
		setViewText(R.id.main_count_text, message);
		findViewById(R.id.main_counting_text).setVisibility(View.GONE);
	}

	/**
	 * デマ通報結果
	 * @param	count	件数
	 */
	private void onMsgNotifyDema(int count) {
		// プログレス表示を消す
		if (mProgress != null) {
			mProgress.dismiss();
			mProgress = null;
		}

		int result = R.string.report_failure;
		if (count > 0) {
			// 成功したらツイートIDを記録しておく
			saveReportTweet(mTweetID);
			// デマ件数更新
			onMsgGetCount(count);
			result = R.string.report_success;
		}

		// 結果表示
		new AlertDialog.Builder(this)
			.setMessage(result)
			.setPositiveButton(R.string.report_result_ok, new DialogInterface.OnClickListener() {
					public void onClick(DialogInterface dialog, int which) {
						dialog.dismiss();
					}
				})
			.show();
	}

	/**
	 * ツイートをデモ通報済みか判定
	 * @param	id	ツイートID
	 * @return	通報済み状態
	 */
	private boolean idReportTweet(String id) {
		// 通報済みツイート走査
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
		String report[] = pref.getString(PREF_REPORT_TWEET, "").split(REPORT_DELIMITER);
		for (int index = 0; index < report.length; index++) {
			if (id.equals(report[index])) {
				// 通報済み
				return true;
			}
		}
		// 通報してないよ
		return false;
	}

	/**
	 * デモ通報したツイートを保存
	 * @param	id	ツイートID
	 */
	private void saveReportTweet(String id) {
		SharedPreferences pref = PreferenceManager.getDefaultSharedPreferences(this);
		String report[] = pref.getString(PREF_REPORT_TWEET, "").split(REPORT_DELIMITER);

		// 新しい通報済みレポートリスト
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
				onMsgGetCount(msg.arg1);
				break;

			case MSG_NOTIFYDEMA:		// デマ通報
				onMsgNotifyDema(msg.arg1);
				break;
			}
		}
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
