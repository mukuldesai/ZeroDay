import { useState } from 'react'
import { copyToClipboard } from '../utils/clipboard'

export function useCopyToClipboard() {
  const [isCopied, setIsCopied] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const copy = async (text: string, successMessage?: string) => {
    setIsLoading(true)
    const success = await copyToClipboard(text, successMessage)
    setIsCopied(success)
    setIsLoading(false)

    if (success) {
      setTimeout(() => setIsCopied(false), 2000)
    }
    
    return success
  }

  return {
    copy,
    isCopied,
    isLoading
  }
}