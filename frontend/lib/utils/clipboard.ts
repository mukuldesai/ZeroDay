import { toast } from 'react-hot-toast'

export const copyToClipboard = async (text: string, successMessage?: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    toast.success(successMessage || 'Copied to clipboard!')
    return true
  } catch (error) {
   
    try {
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      textArea.remove()
      toast.success(successMessage || 'Copied to clipboard!')
      return true
    } catch (fallbackError) {
      toast.error('Failed to copy to clipboard')
      return false
    }
  }
}

export const readFromClipboard = async (): Promise<string | null> => {
  try {
    const text = await navigator.clipboard.readText()
    return text
  } catch (error) {
    toast.error('Failed to read from clipboard')
    return null
  }
}