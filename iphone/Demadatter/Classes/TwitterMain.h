//
//  TwitterMain.h
//  Demadatter
//
//  Created by Yoshiaki NAKANISHI on 11/03/21.
//  Copyright 2011 ブライテクノ株式会社. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "MGTwitterEngine.h"


@interface TwitterMain : NSObject <MGTwitterEngineDelegate> {
    @private
    NSString *consumerKey;
    NSString *consumerSecret;
    
    MGTwitterEngine *twitterEngine;
    OAToken *token;
}

@end
