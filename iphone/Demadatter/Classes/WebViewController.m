//
//  WebViewController.m
//  Demadatter
//
//  Created by mochida rei on 11/04/03.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "WebViewController.h"


@implementation WebViewController

@synthesize web;

- (void)webViewDidStartLoad:(UIWebView *)webView {
    [UIApplication sharedApplication].networkActivityIndicatorVisible = YES;
}

- (void)webViewDidFinishLoad:(UIWebView *)webView {
    [UIApplication sharedApplication].networkActivityIndicatorVisible = NO;
	NSURLRequest *_request = webView.request;
	NSURL *url = _request.URL;
	NSLog(@"URL:%@",[url absoluteURL]);
	NSLog(@"method:%@",[_request HTTPMethod]);
	NSLog(@"http body:%@",[[[NSString alloc] initWithData:[_request HTTPBody] encoding:NSUTF8StringEncoding] stringByReplacingPercentEscapesUsingEncoding:NSUTF8StringEncoding]);
}

- (BOOL)webView:(UIWebView *)webView shouldStartLoadWithRequest:(NSURLRequest *)request navigationType:(UIWebViewNavigationType)navigationType {
	NSURL *url = request.URL;
	NSLog(@"URL2:%@",[url absoluteURL]);
	NSLog(@"method2:%@",[request HTTPMethod]);	
	NSLog(@"http2 body:%@",[[[NSString alloc] initWithData:[request HTTPBody] encoding:NSUTF8StringEncoding] stringByReplacingPercentEscapesUsingEncoding:NSUTF8StringEncoding]);
	return YES;
}

// The designated initializer.  Override if you create the controller programmatically and want to perform customization that is not appropriate for viewDidLoad.
/*
- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization.
    }
    return self;
}
*/

// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
    [super viewDidLoad];
	[self.navigationController setNavigationBarHidden:YES animated:NO];
	cRequest = [[[NSURLRequest alloc] initWithURL:[NSURL URLWithString:@"http://1000.demadatter-dev.appspot.com/"]] retain];
	[web loadRequest:cRequest];
}

/*
// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations.
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}
*/

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
}

- (void)viewDidUnload {
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}


- (void)dealloc {
	[cRequest release];
	[web release];
    [super dealloc];
}


@end
