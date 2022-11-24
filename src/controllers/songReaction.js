import { performance } from 'perf_hooks'
import { logger, metrics } from '@whatagoodbot/utilities'

export default async (payload, spotify) => {
  const startTime = performance.now()

  if (payload.nowPlaying.provider === 'spotify' && payload.reaction === 'star' && payload.room.spotify.starredPlaylist) {
    const functionName = 'saveStarred Track'
    logger.debug({ event: functionName })
    metrics.count(functionName)
    const starredTracks = await spotify.getPlaylist(payload.room.spotify.starredPlaylist)
    const starredTrackIds = starredTracks.items.map(starredTrack => starredTrack.track.uri)
    if (!starredTrackIds.includes(payload.nowPlaying.uri)) {
      spotify.addToPlaylist(payload.room.spotify.starredPlaylist, [payload.nowPlaying.uri])
      metrics.trackExecution(functionName, 'function', performance.now() - startTime, true)
      logger.debug({ event: functionName })
    } else {
      logger.debug({ event: 'Restarred Song' })
      metrics.count('restarredSong')
    }
  }
}
