import genre from '../functions/genre.js'
import relink from '../functions/relink.js'
import seeds from '../functions/seeds.js'

const functions = {
  askbeav: genre,
  genre,
  relink,
  seeds
}

export default (payload, spotify) => {
  if (payload.service === process.env.npm_package_name) return functions[payload.command](payload, spotify)
}
