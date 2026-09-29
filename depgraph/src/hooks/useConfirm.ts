'use client'
import { useCallback, useEffect, useRef, useState } from 'react'

export function useConfirm(ms = 3000) {
  const [armedKey, setArmedKey] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current)
    },
    [],
  )

  const press = (key: string, action: () => void) => {
    if (timer.current) clearTimeout(timer.current)
    timer.current = null
    if (armedKey === key) {
      setArmedKey(null)
      action()
      return
    }
    setArmedKey(key)
    timer.current = setTimeout(() => setArmedKey(null), ms)
  }

  const isArmed = (key: string) => armedKey === key

  const reset = useCallback(() => {
    if (timer.current) clearTimeout(timer.current)
    timer.current = null
    setArmedKey(null)
  }, [])

  return { isArmed, press, reset }
}
