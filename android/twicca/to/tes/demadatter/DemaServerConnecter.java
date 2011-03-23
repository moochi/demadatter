package to.tes.demadatter;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import android.os.Handler;
import android.os.Message;

public class DemaServerConnecter {
	private URL server_url;
	private Handler handle;

	public DemaServerConnecter(URL url) {
		// TODO 自動生成されたコンストラクター・スタブ
		server_url = url;
	}
	
	public void getDemaCount(String id, String tweet, String screen_user_name, String create_at, Message msg)
	{
		this.handle = msg.getTarget();
		// レポート数を取得する
		new Thread(new Runnable() {
			@Override
			public void run() {
				try{
					HttpURLConnection http = (HttpURLConnection)server_url.openConnection();
					http.setRequestMethod("GET");
					http.connect();
					InputStream in = http.getInputStream();
					byte b[] = new byte[http.getContentLength()];
					in.read(b);
					in.close();
					http.disconnect();
					// テストコード
					Message ret = new Message();
					ret.arg1 = 12345;
					handle.sendMessage(ret);
				}catch(Exception e){
					
				}
			}
		}).start();
	}
	
	public void notifyDema(String id, String tweet, String screen_user_name, String create_at, Message msg)
	{
		// レポートを送信する
	}

}
