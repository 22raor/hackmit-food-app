//
//  AuthViewModel.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//


import SwiftUI
import GoogleSignIn
import GoogleSignInSwift

class AuthViewModel: ObservableObject {
    @Published var userSignedIn = false
    @Published var idToken: String? = nil

    func signIn() {
        guard let rootVC = UIApplication.shared.connectedScenes
                .compactMap({ ($0 as? UIWindowScene)?.windows.first?.rootViewController })
                .first else { return }

        GIDSignIn.sharedInstance.signIn(withPresenting: rootVC) { signInResult, error in
            guard error == nil, let signInResult = signInResult else { return }

            // Refresh ID token if needed
            signInResult.user.refreshTokensIfNeeded { user, error in
                guard error == nil, let user = user else { return }

                DispatchQueue.main.async {
                    self.idToken = user.idToken?.tokenString
                    self.userSignedIn = true
                    print("Fresh JWT: \(user.idToken?.tokenString ?? "none")")
                }
            }
        }
    }

    func signOut() {
        GIDSignIn.sharedInstance.signOut()
        self.idToken = nil
        self.userSignedIn = false
    }
}
