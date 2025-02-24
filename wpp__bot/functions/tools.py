produtos = [
    {
        "nome_produto": "Mesa Redonda de Canto Nápoles",
        "medidas": "Altura: 75cm, Diâmetro: 60cm",
        "preco": 250.00,
        "disponibilidade": "Disponível"
    },
    {
        "nome_produto": "Prateleira Decorativa Luxo",
        "medidas": "Comprimento: 80cm, Largura: 20cm, Altura: 3cm",
        "preco": 120.00,
        "disponibilidade": "Disponível"
    },
    {
        "nome_produto": "Escrivaninha Compacta Home Office",
        "medidas": "Comprimento: 120cm, Largura: 60cm, Altura: 75cm",
        "preco": 200.00,
        "disponibilidade": "Indisponível"
    },
    {
        "nome_produto": "Sapateira Multifuncional Moderna",
        "medidas": "Altura: 100cm, Largura: 50cm, Profundidade: 30cm",
        "preco": 350.00,
        "disponibilidade": "Disponível"
    },
    {
        "nome_produto": "Penteadeira Elegance com Espelho",
        "medidas": "Comprimento: 90cm, Largura: 40cm, Altura: 75cm",
        "preco": 70.00,
        "disponibilidade": "Disponível"
    }
]

system = ("Você é um assistente especializado em extrair e organizar informações essenciais de conversas com clientes. "
                "Sua tarefa é identificar e listar as seguintes informações, se disponíveis:\n"
                "- Nome do cliente\n"
                "- Número do pedido\n"
                "- Canal de compra (ex.: Shopee, Mercado Livre)\n"
                "- Problema relatado\n\n"
                "Se alguma informação estiver ausente, liste-a como 'Faltando'.\n"
                "\nApós organizar as informações, avalie se a intervenção de um atendente é necessária e responda apenas 'Sim' ou 'Não'.\n\n"
                "Critérios para intervenção de atendente:\n"
                "- Necessário para finalizar compras.\n"
                "- Necessário em dúvidas sobre envio, produtos danificados, ou qualquer situação em que você não saiba como prosseguir.\n\n"
                "Formato da saída:\n"
                "1. Nome do Cliente: [Nome ou 'Faltando']\n"
                "2. Número do Pedido: [Número ou 'Faltando']\n"
                "3. Canal de Compra: [Canal ou 'Faltando']\n"
                "4. Problema Relatado: [Descrição]\n"
                "5. Intervenção de Atendente Necessária: [Sim/Não]\n\n"
                "5. Resumo do atendimento: [Resumo da intenção do cliente]\n\n"
                "O texto deve ser claro e bem formatado para fácil leitura.")