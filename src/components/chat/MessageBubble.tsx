import type { Message } from '../../types'
import { UserBubble } from './UserBubble'
import { JamesBubble } from './JamesBubble'

interface Props {
  message: Message
  userQuery: string
}

export function MessageBubble({ message, userQuery }: Props) {
  if (message.role === 'user') return <UserBubble message={message} />
  return <JamesBubble message={message} userQuery={userQuery} />
}
