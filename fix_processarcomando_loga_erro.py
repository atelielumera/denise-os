import pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent
feitos = []

def replace_once(path, old, new, label):
    p = BASE / path
    s = p.read_text(encoding='utf-8')
    n = s.count(old)
    if n != 1:
        print(f"ABORTADO ({label}): esperava 1 ocorrencia, encontrei {n}. Nada foi alterado.")
        sys.exit(1)
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    feitos.append(label)

# processarComando engolia qualquer erro (classificador falhar, Supabase falhar, JSON invalido, etc)
# sem deixar rastro nenhum - a partir de agora fica registrado no log.
replace_once(
    'api/whatsapp-webhook.js',
    """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch {
    return null
  }
}""",
    """    await supabase.from('app_snapshot').upsert({ id: 'denise', data: d, updated_at: new Date().toISOString() })
    return partesConfirmacao.join('\\n')
  } catch (errProcessar) {
    console.error('Erro ao processar comando estruturado do WhatsApp (caiu no chat livre sem registrar nada):', errProcessar?.message || errProcessar)
    return null
  }
}""",
    'webhook-processarcomando-loga-erro'
)

print('TUDO OK:', feitos)
