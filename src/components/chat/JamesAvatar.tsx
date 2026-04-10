import { useState } from 'react'

export function JamesAvatar({ size = 32 }: { size?: number }) {
  const [imgError, setImgError] = useState(false)

  if (imgError) {
    return (
      <div
        className="rounded-full bg-james-primary flex items-center justify-center shrink-0 font-bold text-white"
        style={{ width: size, height: size, fontSize: size * 0.38 }}
      >
        J
      </div>
    )
  }

  return (
    <img
      src="/james-avatar.png"
      alt="James"
      className="rounded-full object-cover shrink-0"
      style={{ width: size, height: size }}
      onError={() => setImgError(true)}
    />
  )
}
