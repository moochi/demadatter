//
//  DemadatterAppDelegate.h
//  Demadatter
//
//  Created by Yoshiaki NAKANISHI on 11/03/21.
//  Copyright 2011 ブライテクノ株式会社. All rights reserved.
//

#import <UIKit/UIKit.h>

@class DemadatterViewController;

@interface DemadatterAppDelegate : NSObject <UIApplicationDelegate> {
    UIWindow *window;
    DemadatterViewController *viewController;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet DemadatterViewController *viewController;

@end

