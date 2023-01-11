#!/bin/bash

## @TODO corrigir o parseamento dessa página
# https://wiki.openstreetmap.org/wiki/Cidades_brasileiras_com_mapeamento_deficit%C3%A1rio
wiki_as_base --input-autodetect 'Cidades_brasileiras_com_mapeamento_deficitário' --verbose

# @TODO criar rotina para extrar links externos?
wiki_as_base --input-autodetect 'Pt:Canais_para_contato' --verbose
