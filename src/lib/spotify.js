import { logger } from '@whatagoodbot/utilities'
import SpotifyWebApi from 'spotify-web-api-node'

const redirectUri = 'http://whatagoodbot.com/test-callback'

export default class SpotifyClient {
  constructor (clientId, clientSecret) {
    this.api = new SpotifyWebApi({ clientId, clientSecret, redirectUri })
    this.refreshAccessToken = null
    this.api.setRefreshToken(process.env.TOKEN_EXTERNAL_SPOTIFY || 'AQCHYf3upvrAUuGSOlxFnkJ4by857MVgu8qZnlrGZymvcTgjsnW76W7FcCCojs6N4sP9MfLlau-fFaHQlo8n42TTi-GGjF10hXs5Z0417TVQzclF4pcYmbVlgddTyjsKigU')
    this.setAccessToken()
  }

  tearDown () {
    clearTimeout(this.refreshAccessToken)
  }

  setAccessToken () {
    const self = this
    this.api.refreshAccessToken()
      .then(data => {
        logger.debug('The access token has been refreshed!')
        self.api.setAccessToken(data.body.access_token)
        if (self.refreshAccessToken) {
          clearTimeout(self.refreshAccessToken)
          self.refreshAccessToken = undefined
        }

        const expiresIn = data.body.expires_in
        const accessToken = data.body.access_token

        // Save the access token so that it's used in future calls
        self.api.setAccessToken(accessToken)

        /* Refresh when it expires. May want to call on 401 as well */
        self.refreshAccessToken = setTimeout(
          self.setAccessToken.bind(self),
          expiresIn * 1000
        )
      })
  }

  addToPlaylist (playlist, tracks) {
    return new Promise(resolve => {
      this.api
        .addTracksToPlaylist(playlist, tracks)
        .then(resolve)
    })
  }

  getPlaylist (id) {
    return new Promise(resolve => {
      this.api
        .getPlaylist(id)
        .then(({ body }) => {
          const {
            tracks: { items },
            name
          } = body

          if (items.length === 0) {
            throw new Error('Playlist does not contain any tracks.')
          }

          const results = { name, items }
          resolve(results)
        })
        .catch((err) => {
          if (err.statusCode === 401) {
            this.setAccessToken()
          } else {
            console.error('getPlaylist', id, err)
            resolve()
          }
        })
    })
  }

  getTrack (id) {
    return new Promise(resolve => {
      this.api
        .getTrack(id)
        .then(({ body }) => {
          resolve(body)
        })
        .catch((err) => {
          if (err.statusCode === 401) {
            this.setAccessToken()
          } else {
            console.error('getTrack', id, err)
          }
          resolve(err.body)
        })
    })
  }

  getArtist (id) {
    return new Promise(resolve => {
      this.api
        .getArtist(id)
        .then(({ body }) => {
          resolve(body)
        })
        .catch((err) => {
          if (err.statusCode === 401) {
            this.setAccessToken()
          } else {
            console.error('getArtist', id, err)
          }
          resolve(err.body)
        })
    })
  }

  getAudioFeatures (id) {
    return new Promise(resolve => {
      this.api
        .getAudioFeaturesForTrack(id)
        .then(({ body }) => {
          resolve(body)
        })
        .catch((err) => {
          if (err.statusCode === 401) {
            this.setAccessToken()
          } else {
            console.error('getAudioFeatures', id, err)
          }
          resolve(err.body)
        })
    })
  }

  getRecommendations (params) {
    // const params = {
    //   min_energy: 0.4,
    //   seed_artists: seedArtists,
    //   min_popularity: 50,
    // }
    return new Promise(resolve => {
      this.api.getRecommendations(params).then(
        data => {
          const recommendations = data.body
          resolve(recommendations)
        },
        err => {
          console.log(err)
          logger.debug('Something went wrong!', err)
          resolve()
        }
      )
    })
  }

  getRecommendationGenres () {
    return new Promise(resolve => {
      this.api.getAvailableGenreSeeds().then(
        (data) => {
          const genreSeeds = data.body
          resolve(genreSeeds)
        },
        (err) => {
          logger.debug('Something went wrong!', err)
          resolve()
        }
      )
    })
  }
}
