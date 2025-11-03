# 🎨 Instruções para Ícones da Extensão

## Nota Importante

Os ícones da extensão estão atualmente em formato SVG (icon-48.svg e icon-96.svg).

O Firefox aceita SVG, mas para melhor compatibilidade, você pode convertê-los para PNG.

## Opção 1: Converter SVG para PNG

### Usando ImageMagick (Linux/Mac)

```bash
cd extension/icons

# Converter icon-48.svg para PNG
convert -background none icon-48.svg icon-48.png

# Converter icon-96.svg para PNG
convert -background none icon-96.svg icon-96.png
```

### Usando Inkscape

```bash
# icon-48.png
inkscape icon-48.svg --export-filename=icon-48.png --export-width=48 --export-height=48

# icon-96.png
inkscape icon-96.svg --export-filename=icon-96.png --export-width=96 --export-height=96
```

### Usando Online

Acesse: https://convertio.co/svg-png/

1. Upload dos arquivos SVG
2. Converta para PNG
3. Faça download
4. Coloque na pasta extension/icons/

## Opção 2: Criar Ícones Personalizados

Você pode criar seus próprios ícones usando:

- **Figma**: https://figma.com
- **Canva**: https://canva.com
- **GIMP**: Software gratuito de edição de imagens
- **Photoshop**: Se tiver acesso

### Especificações

- **icon-48.png**: 48x48 pixels
- **icon-96.png**: 96x96 pixels
- **Formato**: PNG com transparência
- **Tema**: Escudo de proteção (🛡️) com gradiente roxo/azul

### Sugestão de Design

1. Fundo: Gradiente de #667eea para #764ba2
2. Ícone: Escudo ou cadeado branco
3. Bordas arredondadas
4. Sombra sutil

## Opção 3: Usar Emoji como Ícone

Os SVGs atuais usam o emoji 🛡️, que funciona bem no Firefox.

Se quiser manter assim, não precisa fazer nada!

## Atualizar manifest.json

Após criar os PNGs, o manifest.json já está configurado para usá-los:

```json
"icons": {
  "48": "icons/icon-48.png",
  "96": "icons/icon-96.png"
}
```

## 🎨 Recursos Gratuitos de Ícones

- **Flaticon**: https://flaticon.com
- **Icons8**: https://icons8.com
- **Heroicons**: https://heroicons.com
- **Feather Icons**: https://feathericons.com

Busque por: "shield", "security", "protection", "lock"

---

**Nota**: Os ícones SVG funcionam perfeitamente no Firefox para fins de demonstração e avaliação. A conversão para PNG é opcional e serve apenas para melhorar a aparência visual.
