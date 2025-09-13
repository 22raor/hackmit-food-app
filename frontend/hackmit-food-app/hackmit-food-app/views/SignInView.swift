//
//  SignInView.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//


import SwiftUI
import GoogleSignInSwift

struct SignInView: View {
    @EnvironmentObject var auth: AuthViewModel

    var body: some View {
        VStack(spacing: 20) {
            Text("Welcome! Please sign in")
                .font(.title)
            GoogleSignInButton(action: {
                auth.signIn()
            })
            .frame(height: 50)
            .padding(.horizontal)
        }
    }
}
