#!/bin/bash

echo "=========================================="
echo "MANUELA METAIS - Sistema de Gestão"
echo "=========================================="
echo ""
echo "Instalando dependências..."
pip install -q -r requirements.txt

echo ""
echo "✅ Dependências instaladas!"
echo ""
echo "Iniciando servidor..."
echo ""
echo "🌐 Acesse o sistema em: http://localhost:5000"
echo ""
echo "⚠️  IMPORTANTE:"
echo "- Faça backup do arquivo data.json diariamente"
echo "- Leia o README.md antes de usar em produção"
echo "- Este sistema NÃO tem autenticação ou backup automático"
echo ""
echo "Pressione CTRL+C para encerrar o servidor"
echo "=========================================="
echo ""

python app.py
