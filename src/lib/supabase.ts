import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  'https://pvqvlqdciblelsngaogw.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2cXZscWRjaWJsZWxzbmdhb2d3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ5MTAxMTUsImV4cCI6MjEwMDQ4NjExNX0.IO5xFmVZwktJOiZPcoCkuUWxXIf8x7qSl5QXsYoankU'
)
