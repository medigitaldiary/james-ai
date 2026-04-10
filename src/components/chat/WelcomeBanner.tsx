export function WelcomeBanner() {
  return (
    <div className="flex flex-col items-center pt-16 pb-8 px-4 text-center">
      {/* JAMES AI badge */}
      <div className="mb-6">
        <img src="/james-icon.png?v=2" alt="James AI" className="h-12" />
      </div>

      {/* Heading */}
      <h1 className="text-james-text font-semibold text-3xl leading-tight max-w-md">
        Hey, how may I assist you today?
      </h1>
    </div>
  )
}
