// pages/_app.tsx
import '../styles/global.css'
import type { AppProps } from 'next/app'
import Head from 'next/head'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>ZeroDay</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="Agentic AI for developer onboarding – fast, smart, contextual" />
        <meta name="theme-color" content="#3b82f6" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Component {...pageProps} />
    </>
  )
}
