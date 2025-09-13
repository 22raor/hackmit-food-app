//
//  MenuItem.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//

import Foundation

struct MenuItem : Identifiable {
    let id = UUID()
    let name: String
    let imageName: String
    let price: Double
}
