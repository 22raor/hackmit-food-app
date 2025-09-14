//
//  AuthViewModel.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//


import SwiftUI
import GoogleSignIn
import GoogleSignInSwift
import OpenAPIURLSession
import OpenAPIRuntime

class AuthViewModel: ObservableObject {
    @Published var userSignedIn = false
    @Published var idToken: String? = nil
    @Published var client: Client? = nil
    
    func exchangeGoogleTokenForBackendAuth(googleIdToken: String) async throws {
        guard let serverURL = try? Servers.Server1.url() else {
            throw NSError(domain: "AuthError", code: 1, userInfo: [NSLocalizedDescriptionKey: "Invalid server URL"])
        }
        
        print(googleIdToken)
        
        let tempClient = Client(serverURL: serverURL, transport: URLSessionTransport())
        
        do {
            let response = try await tempClient.googleAuthAuthGooglePost(
                .init(body: .json(Components.Schemas.GoogleAuthRequest(idToken: googleIdToken)))
            )
            print("Decoded response: \(response)")
        } catch {
            print("Error: \(error)")
        }
        
        let response = try await tempClient.googleAuthAuthGooglePost(
                .init(body: .json(Components.Schemas.GoogleAuthRequest(idToken: googleIdToken)))
            )
                
        switch response {
        case .ok(let success):
            if case .json(let loginResponse) = success.body {
                let backendToken = loginResponse.accessToken

                let authedClient = Client(
                    serverURL: serverURL,
                    transport: URLSessionTransport(),
                    middlewares: [BearerAuthenticationMiddleware(token: backendToken)]
                )

                DispatchQueue.main.async {
                    self.client = authedClient
                    self.userSignedIn = true
                }
                return
            }

        case .unauthorized(_):
            throw NSError(domain: "AuthError", code: 2, userInfo: [NSLocalizedDescriptionKey: "Token exchange failed"])
        case .unprocessableContent(_):
            throw NSError(domain: "AuthError", code: 3, userInfo: [NSLocalizedDescriptionKey: "Invalid token"])
        case .undocumented(let statusCode, _):
            throw NSError(domain: "AuthError", code: 4, userInfo: [NSLocalizedDescriptionKey: "Unexpected response: \(statusCode)"])
        }
    }

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
                        Task {
                            do {
                                if let googleIdToken = user.idToken?.tokenString {
                                    try await self.exchangeGoogleTokenForBackendAuth(googleIdToken: googleIdToken)
                                    print("Successfully authenticated with backend")
                                }
                            } catch {
                                print("Authentication failed: \(error.localizedDescription)")
                                self.userSignedIn = false
                            }
                        }
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
