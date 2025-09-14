import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import { components } from "./types/api-types"

type GoogleAuthRequest = components["schemas"]["GoogleAuthRequest"]
type LoginResponse = components["schemas"]["LoginResponse"]

declare module "next-auth" {
  interface Session {
    access_token?: string
    is_new_user?: boolean
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    })
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (account?.provider === "google" && account?.id_token) {
        try {
          const response = await fetch(`${process.env.BACKEND_URL}/auth/google`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              id_token: account.id_token
            } as GoogleAuthRequest),
          })

          if (response.ok) {
            const backendData: LoginResponse = await response.json()
            token.access_token = backendData.access_token
            token.user = backendData.user
            token.is_new_user = backendData.is_new_user
          }
        } catch (error) {
          console.error('Backend authentication failed:', error)
        }
      }

      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.access_token = token.access_token as string
        session.user = token.user ? { ...session.user, ...token.user } : session.user
        session.is_new_user = token.is_new_user as boolean
      }
      return session
    },
  },
})
