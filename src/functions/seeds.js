import { logger, metrics } from '@whatagoodbot/utilities'

export default async (payload, spotify) => {
  const functionName = 'seeds'
  const startTime = performance.now()
  logger.debug({ event: functionName })

  if (!payload.seedTracks) return
  payload.service = payload.client.name
  payload.command = 'updateBotPlaylist'
  const spotifyResults = await spotify.getRecommendations({ seed_tracks: payload.seedTracks })
  payload.nextTracks = spotifyResults.tracks

  metrics.trackExecution(functionName, 'mqtt', performance.now() - startTime, true)

  return [{
    topic: 'externalRequest',
    payload
  }]
}
