//
//  MenuCardView.swift
//  hackmit-food-app
//
//  Created by Arvindh Manian on 9/13/25.
//

import SwiftUICore
import SwiftUI


struct MenuCardView: View {
    let item: MenuItem
    
    var body: some View {
        VStack(alignment: .leading) {
            Image(item.imageName)
                .resizable()
                .scaledToFill()
                .frame(height: 200)
                .clipped()
                .cornerRadius(13)
            
            Text(item.name)
                .font(.title)
                .padding(.top, 5)
            
            Text(String(format: "$%.2f", item.price))
                .font(.subheadline)
                .bold()
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(30)
        .shadow(radius: 5)
    }
}


#Preview {
    MenuCardView(item: MenuItem(name: "Chicken Tikka Masala", imageName: "chicken_tikka", price: 123.45))
}
