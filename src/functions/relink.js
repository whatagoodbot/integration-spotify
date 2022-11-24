import { clients } from '@whatagoodbot/rpc'
import { logger, metrics } from '@whatagoodbot/utilities'

import spotifyMarkets from '../../config/spotifyMarkets.js'

export default async (payload, spotify) => {
  const functionName = 'relink'
  const startTime = performance.now()

  let message
  const strings = await clients.strings.getMany(['spotifyNoTrackFound', 'spotifyAvailableAll', 'spotifyAvailableIn', 'spotifyNotAvailableIn'])
  if (payload.nowPlaying.provider === 'spotify' && payload.nowPlaying.id) {
    const trackDetails = await spotify.getTrack(payload.nowPlaying.id)
    const availableMarkets = trackDetails.available_markets
    if (availableMarkets.length === 0) {
      message = strings.spotifyNoTrackFound
    } else {
      const filteredMarkets = spotifyMarkets.filter(market => market.include)
      const differences = filteredMarkets.filter(market => !availableMarkets.includes(market.code))
      if (differences.length) {
        if (differences.length > availableMarkets.length) {
          const differencesPositive = filteredMarkets.filter(market => availableMarkets.includes(market.code))
          const availableRegions = differencesPositive.map((difference) => {
            return difference.name
          })
          message = `${strings.spotifyAvailableIn} ${availableRegions.join(', ')}`
        } else {
          const unavailableRegions = differences.map((difference) => {
            return difference.name
          })
          message = `${strings.spotifyNotAvailableIn} ${unavailableRegions.join(', ')}`
        }
      } else {
        message = strings.spotifyAvailableAll
      }
    }
  } else {
    message = strings.spotifyNoTrackFound
  }
  logger.debug({ event: functionName })
  metrics.trackExecution(functionName, 'mqtt', performance.now() - startTime, true)

  return [{
    topic: 'broadcast',
    payload: {
      message
    }
  }]
}
