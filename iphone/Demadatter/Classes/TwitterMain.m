//
//  TwitterMain.m
//  Demadatter
//
//  Created by Yoshiaki NAKANISHI on 11/03/21.
//

#import "TwitterMain.h"

@interface TwitterMain ()
@property (nonatomic, retain) NSString *consumerKey;
@property (nonatomic, retain) NSString *consumerSecret;
@end

@implementation TwitterMain

@synthesize consumerKey;
@synthesize consumerSecret;

- (id) init {
    if (self = [super init]) {
        self.consumerKey = @"BXt2iZGEyLfXkn9i0gjSw";
        self.consumerSecret = @"y6WsVEHLINdiQRCuxQZzseCUlKFSBzb4PmCOgjgpQ";
    }
    
    return self;
}

- (BOOL) login:(NSString *)username password:(NSString *)password {
    if (username == nil || password == nil) {
        return NO;
    }
    
    twitterEngine = [[MGTwitterEngine alloc] initWithDelegate:self];
    [twitterEngine setUsesSecureConnection:NO];
    [twitterEngine setConsumerKey:consumerKey secret:consumerSecret];
    [twitterEngine setUsername:username];
    
	if ([twitterEngine getXAuthAccessTokenForUsername:username password:password] == nil) {
        return NO;
    }
    
    return YES;
}

- (BOOL) restoreAccessToken {
    OAToken *aToken;
    
    // read access token from local storage

    token = [aToken retain];
    
    twitterEngine = [[MGTwitterEngine alloc] initWithDelegate:self];
    [twitterEngine setAccessToken:token];
    
    return YES;
}

- (void) release {
    [token release];
    [twitterEngine release];
    [consumerSecret release];
    [consumerKey release];
}

#pragma mark MGTwitterEngineDelegate methods

- (void)requestSucceeded:(NSString *)connectionIdentifier
{
    NSLog(@"Request succeeded for connectionIdentifier = %@", connectionIdentifier);
}


- (void)requestFailed:(NSString *)connectionIdentifier withError:(NSError *)error
{
    NSLog(@"Request failed for connectionIdentifier = %@, error = %@ (%@)", 
          connectionIdentifier, 
          [error localizedDescription], 
          [error userInfo]);
}


- (void)statusesReceived:(NSArray *)statuses forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got statuses for %@:\r%@", connectionIdentifier, statuses);
}


- (void)directMessagesReceived:(NSArray *)messages forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got direct messages for %@:\r%@", connectionIdentifier, messages);
}


- (void)userInfoReceived:(NSArray *)userInfo forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got user info for %@:\r%@", connectionIdentifier, userInfo);
}


- (void)miscInfoReceived:(NSArray *)miscInfo forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got misc info for %@:\r%@", connectionIdentifier, miscInfo);
}


- (void)searchResultsReceived:(NSArray *)searchResults forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got search results for %@:\r%@", connectionIdentifier, searchResults);
}


- (void)socialGraphInfoReceived:(NSArray *)socialGraphInfo forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got social graph results for %@:\r%@", connectionIdentifier, socialGraphInfo);
}

- (void)userListsReceived:(NSArray *)userInfo forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got user lists for %@:\r%@", connectionIdentifier, userInfo);
}

- (void)accessTokenReceived:(OAToken *)aToken forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Access token received! %@",aToken);
    
    token = [aToken retain];
    
    // TODO: store token to local storage
}

#if YAJL_AVAILABLE || TOUCHJSON_AVAILABLE

- (void)receivedObject:(NSDictionary *)dictionary forRequest:(NSString *)connectionIdentifier
{
    NSLog(@"Got an object for %@: %@", connectionIdentifier, dictionary);
}

#endif

@end
