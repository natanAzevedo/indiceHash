import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import {Badge} from "@/components/ui/badge"

interface HashVisualizationProps {
    tableData: {
        total_tuplas: number
        total_paginas: number
    }
    statistics: {
        total_buckets: number
        total_registros: number
        total_colisoes: number
        taxa_colisoes: number      // Mudança: removido o "(%) "
        total_overflows: number
        taxa_overflows: number     // Mudança: removido o "(%)"
        fator_carga: number        // Campo adicionado
    } | null
    isIndexBuilt: boolean
}

export function HashVisualization({tableData, statistics, isIndexBuilt}: HashVisualizationProps) {
    const renderHashTable = () => {
        if (!statistics) return null

        const buckets = Array.from({length: Math.min(statistics.total_buckets, 20)}, (_, i) => i)

        return (
            <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-10 gap-2">
                {buckets.map((bucket) => (
                    <div
                        key={bucket}
                        className="aspect-square border-2 border-gray-300 rounded-lg flex items-center justify-center text-xs font-mono bg-white hover:bg-blue-50 transition-colors"
                    >
                        <div className="text-center">
                            <div className="text-gray-600">B{bucket}</div>
                            <div className="w-2 h-2 bg-blue-500 rounded-full mx-auto mt-1"></div>
                        </div>
                    </div>
                ))}
                {statistics.total_buckets > 20 && (
                    <div
                        className="aspect-square border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-xs text-gray-500">
                        +{statistics.total_buckets - 20}
                    </div>
                )}
            </div>
        )
    }

    const renderPages = () => {
        const pages = Array.from({length: Math.min(tableData.total_paginas, 12)}, (_, i) => i)

        return (
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {pages.map((page) => (
                    <div
                        key={page}
                        className="aspect-[3/4] border-2 border-gray-300 rounded-lg p-2 bg-white hover:bg-green-50 transition-colors"
                    >
                        <div className="text-xs font-semibold text-gray-700 mb-1">Página {page}</div>
                        <div className="space-y-1">
                            {Array.from({length: 4}).map((_, i) => (
                                <div key={i} className="h-1 bg-gray-200 rounded"></div>
                            ))}
                        </div>
                    </div>
                ))}
                {tableData.total_paginas > 12 && (
                    <div
                        className="aspect-[3/4] border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-xs text-gray-500">
                        +{tableData.total_paginas - 12}
                    </div>
                )}
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Data Structure Overview */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        Estrutura de Dados - Páginas da Tabela
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex flex-wrap gap-2">
                            <Badge variant="outline">Total: {tableData.total_paginas} páginas</Badge>
                            <Badge variant="outline">Tuplas: {tableData.total_tuplas.toLocaleString()}</Badge>
                        </div>
                        {renderPages()}
                    </div>
                </CardContent>
            </Card>

            {/* Hash Index Structure */}
            {isIndexBuilt && statistics && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                            Estrutura do Índice Hash
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex flex-wrap gap-2">
                                <Badge variant="outline">Buckets: {statistics.total_buckets}</Badge>
                                <Badge variant="outline">
                                    Fator de Carga: {statistics.fator_carga?.toFixed(2) || 'N/A'}
                                </Badge>
                                <Badge
                                    variant="outline"
                                    className={statistics.taxa_colisoes > 10 ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}
                                >
                                    Colisões: {statistics.taxa_colisoes?.toFixed(1) || 0}%
                                </Badge>
                            </div>
                            {renderHashTable()}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Hash Function Explanation */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                        Funcionamento da Função Hash
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm">
                            <div className="text-gray-600 mb-2">Algoritmo:</div>
                            <div>1. hash(chave) = soma_ascii(chave) % total_buckets</div>
                            <div>2. bucket_id = hash(chave)</div>
                            <div>3. pagina_id = bucket[bucket_id]</div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                            <div className="p-4 border rounded-lg">
                                <div className="text-2xl font-bold text-blue-600">Chave</div>
                                <div className="text-sm text-gray-600">Palavra de entrada</div>
                            </div>
                            <div className="p-4 border rounded-lg">
                                <div className="text-2xl font-bold text-purple-600">Hash</div>
                                <div className="text-sm text-gray-600">Função de mapeamento</div>
                            </div>
                            <div className="p-4 border rounded-lg">
                                <div className="text-2xl font-bold text-green-600">Bucket</div>
                                <div className="text-sm text-gray-600">Endereço da página</div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
