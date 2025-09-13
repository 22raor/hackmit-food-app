//
//  hackmit_food_appApp.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//

import SwiftUI
import GoogleSignIn

@main
struct hackmit_food_appApp: App {
    @StateObject var auth = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            AuthWrapperView()
                .environmentObject(auth)
                .onOpenURL { url in
                    GIDSignIn.sharedInstance.handle(url)
                }
        }
    }
}
