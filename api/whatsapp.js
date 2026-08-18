const APP_URL = 'https://denise-os.vercel.app'

function getConfig() {
  const baseUrl = (process.env.EVOLUTION_API_URL || '').replace(/\/+$/, '')
  const apiKey = process.env.EVOLUTION_API_KEY
  const instance = process.env.EVOLUTION_INSTANCE || 'denise-os'
  return { baseUrl, apiKey, instance }
}

async function evoFetch(baseUrl, apiKey, path, opts = {}) {
  const resp = await fetch(baseUrl + path, {
    ...opts,
    headers: { 'content-type': 'application/json', apikey: apiKey, ...(opts.headers || {}) }
  })
  const data = await resp.json().catch(() => ({}))
  return { ok: resp.ok, status: resp.status, data }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Metodo nao permitido.' })
    return
  }
  const { baseUrl, apiKey, instance } = getConfig()
  if (!baseUrl || !apiKey) {
    res.status(500).json({ error: 'Evolution API nao configurada no servidor (EVOLUTION_API_URL / EVOLUTION_API_KEY).' })
    return
  }
  const { action } = req.body || {}

  try {
    if (action === 'status') {
      const r = await evoFetch(baseUrl, apiKey, `/instance/connectionState/${instance}`)
      if (!r.ok) {
        res.status(200).json({ state: 'nao_criada' })
        return
      }
      const state = r.data?.instance?.state || r.data?.state || 'close'
      res.status(200).json({ state })
      return
    }

    if (action === 'connect') {
      let r = await evoFetch(baseUrl, apiKey, `/instance/connect/${instance}`)
      if (!r.ok) {
        await evoFetch(baseUrl, apiKey, '/instance/create', {
          method: 'POST',
          body: JSON.stringify({
            instanceName: instance,
            qrcode: true,
            integration: 'WHATSAPP-BAILEYS',
            webhook: {
              url: `${APP_URL}/api/whatsapp-webhook`,
              byEvents: false,
              base64: true,
              events: ['MESSAGES_UPSERT']
            }
          })
        })
        r = await evoFetch(baseUrl, apiKey, `/instance/connect/${instance}`)
      }
      if (!r.ok) {
        res.status(502).json({ error: r.data?.message || r.data?.error || 'Erro ao conectar a instancia na Evolution API.' })
        return
      }
      const base64 = r.data?.base64 || r.data?.qrcode?.base64 || null
      const pairingCode = r.data?.pairingCode || r.data?.code || null
      if (!base64 && !pairingCode) {
        res.status(200).json({ base64: null, pairingCode: null, message: 'Numero ja pode estar conectado. Verifique o status.' })
        return
      }
      res.status(200).json({ base64, pairingCode })
      return
    }

    if (action === 'logout') {
      await evoFetch(baseUrl, apiKey, `/instance/logout/${instance}`, { method: 'DELETE' })
      res.status(200).json({ ok: true })
      return
    }

    res.status(400).json({ error: 'Acao invalida.' })
  } catch (err) {
    res.status(500).json({ error: 'Falha ao falar com a Evolution API: ' + (err?.message || 'erro desconhecido') })
  }
}
