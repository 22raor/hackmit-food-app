//
//  ContentView 2.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//


//
//  ContentView.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//

import SwiftUI

struct AuthWrapperView: View {
    @EnvironmentObject var auth: AuthViewModel
    var body: some View {
            if auth.userSignedIn {
                ContentView() // Your main app
            } else {
                SignInView() // Only shows sign-in UI
            }
        }
}

#Preview {
    AuthWrapperView()
        .environmentObject(AuthViewModel()) // provide a mock AuthViewModel
}
