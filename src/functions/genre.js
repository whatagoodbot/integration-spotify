import { logger, metrics } from '@whatagoodbot/utilities'
import { clients } from '@whatagoodbot/rpc'

export default async (payload, spotify) => {
  const startTime = performance.now()
  const functionName = 'getCommand'
  logger.debug({ event: functionName })
  metrics.count(functionName)

  if (!payload.nowPlaying.id) {
    const string = await clients.strings.get('spotifyNoTrackFound')
    return [{
      topic: 'broadcast',
      payload: {
        message: string.value
      }
    }]
  }
  const trackDetails = await spotify.getTrack(payload.nowPlaying.id)
  const artist = trackDetails.artists[0].id
  const artistInfo = await spotify.getArtist(artist)

  metrics.trackExecution(functionName, 'mqtt', performance.now() - startTime, true)

  return [{
    topic: 'broadcast',
    payload: {
      message: `Spotify describes ${artistInfo.name} as ${artistInfo.genres.join(', ')}`
    }
  }]
}
