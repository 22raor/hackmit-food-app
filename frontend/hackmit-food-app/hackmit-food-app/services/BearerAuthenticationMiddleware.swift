//
//  BearerAuthenticationMiddleware.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//


import OpenAPIRuntime
import HTTPTypes
import Foundation


struct BearerAuthenticationMiddleware: ClientMiddleware {
    private let token: String
    
    init(token: String) {
        self.token = token
    }
    
    func intercept(
        _ request: HTTPRequest,
        body: HTTPBody?,
        baseURL: URL,
        operationID: String,
        next: (HTTPRequest, HTTPBody?, URL) async throws -> (HTTPResponse, HTTPBody?)
    ) async throws -> (HTTPResponse, HTTPBody?) {
        var authenticatedRequest = request
        authenticatedRequest.headerFields[.authorization] = "Bearer \(token)"
        
        return try await next(authenticatedRequest, body, baseURL)
    }
}
