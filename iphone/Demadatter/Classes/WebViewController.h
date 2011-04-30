//
//  WebViewController.h
//  Demadatter
//
//  Created by mochida rei on 11/04/03.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface WebViewController : UIViewController <UIWebViewDelegate> {
	IBOutlet UIWebView *web;
	NSURLRequest *cRequest;
}

@property(nonatomic,retain) IBOutlet UIWebView *web;

@end
