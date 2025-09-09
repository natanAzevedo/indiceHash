import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import {Badge} from "@/components/ui/badge"
import {Progress} from "@/components/ui/progress"
import {BarChart3, TrendingUp, AlertTriangle, CheckCircle} from "lucide-react"

interface StatisticsPanelProps {
    statistics: {
        total_buckets: number
        total_registros: number
        total_colisoes: number
        taxa_colisoes: number      // Mudança: removido o "(%) "
        total_overflows: number
        taxa_overflows: number     // Mudança: removido o "(%)"
        fator_carga: number        // Campo adicionado
    } | null
    tableData: {
        total_tuplas: number
        total_paginas: number
    }
    searchResult: any
    scanResult: any
}

export function StatisticsPanel({statistics, tableData, searchResult, scanResult}: StatisticsPanelProps) {
    const calculateEfficiency = () => {
        if (!searchResult || !scanResult) return null

        const hashCost = searchResult.custo
        const scanCost = scanResult.custo
        const improvement = (((scanCost - hashCost) / scanCost)).toFixed(1)

        return {
            hashCost,
            scanCost,
            improvement: Number.parseFloat(improvement),
        }
    }

    const efficiency = calculateEfficiency()

    return (
        <div className="space-y-6">
            {/* System Overview */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-600"/>
                        Visão Geral do Sistema
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div
                                className="text-2xl font-bold text-blue-600">{tableData.total_tuplas.toLocaleString()}</div>
                            <div className="text-sm text-gray-600">Total de Registros</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-600">{tableData.total_paginas}</div>
                            <div className="text-sm text-gray-600">Páginas Criadas</div>
                        </div>
                        {statistics && (
                            <>
                                <div className="text-center p-4 bg-purple-50 rounded-lg">
                                    <div className="text-2xl font-bold text-purple-600">{statistics.total_buckets}</div>
                                    <div className="text-sm text-gray-600">Buckets Hash</div>
                                </div>
                                <div className="text-center p-4 bg-orange-50 rounded-lg">
                                    <div
                                        className="text-2xl font-bold text-orange-600">{statistics.fator_carga.toFixed(2)}</div>
                                    <div className="text-sm text-gray-600">Fator de Carga</div>
                                </div>
                            </>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Hash Performance Metrics */}
            {statistics && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-green-600"/>
                            Métricas de Performance do Hash
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm font-medium">Taxa de Colisões</span>
                                    <Badge variant={statistics.taxa_colisoes > 0.1 ? "destructive" : "secondary"}>
                                        {(statistics.taxa_colisoes).toFixed(1)}%
                                    </Badge>
                                </div>
                                <Progress value={statistics.taxa_colisoes} className="h-2"/>
                            </div>

                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm font-medium">Taxa de Overflows</span>
                                    <Badge variant={statistics.taxa_overflows > 0.05 ? "destructive" : "secondary"}>
                                        {(statistics.taxa_overflows).toFixed(1)}%
                                    </Badge>
                                </div>
                                <Progress value={statistics.taxa_overflows} className="h-2"/>
                            </div>

                            <div>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-sm font-medium">Fator de Carga</span>
                                    <Badge variant={statistics.fator_carga > 0.8 ? "destructive" : "secondary"}>
                                        {statistics.fator_carga.toFixed(2)}
                                    </Badge>
                                </div>
                                <Progress value={statistics.fator_carga} className="h-2"/>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="p-4 border rounded-lg text-center">
                                {statistics.taxa_colisoes <= 0.1 ? (
                                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2"/>
                                ) : (
                                    <AlertTriangle className="w-8 h-8 text-yellow-600 mx-auto mb-2"/>
                                )}
                                <div className="text-sm font-medium">Colisões</div>
                                <div
                                    className="text-xs text-gray-600">{statistics.taxa_colisoes <= 0.1 ? "Baixa" : "Alta"}</div>
                            </div>

                            <div className="p-4 border rounded-lg text-center">
                                {statistics.taxa_overflows <= 0.05 ? (
                                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2"/>
                                ) : (
                                    <AlertTriangle className="w-8 h-8 text-yellow-600 mx-auto mb-2"/>
                                )}
                                <div className="text-sm font-medium">Overflows</div>
                                <div
                                    className="text-xs text-gray-600">{statistics.taxa_overflows <= 0.05 ? "Baixo" : "Alto"}</div>
                            </div>

                            <div className="p-4 border rounded-lg text-center">
                                {statistics.fator_carga <= 0.8 ? (
                                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2"/>
                                ) : (
                                    <AlertTriangle className="w-8 h-8 text-yellow-600 mx-auto mb-2"/>
                                )}
                                <div className="text-sm font-medium">Carga</div>
                                <div
                                    className="text-xs text-gray-600">{statistics.fator_carga <= 0.8 ? "Adequada" : "Alta"}</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Performance Comparison */}
            {efficiency && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-blue-600"/>
                            Comparação de Performance
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="text-center p-4 bg-blue-50 rounded-lg">
                                    <div className="text-2xl font-bold text-blue-600">{efficiency.hashCost}</div>
                                    <div className="text-sm text-gray-600">Custo Busca Hash</div>
                                </div>
                                <div className="text-center p-4 bg-red-50 rounded-lg">
                                    <div className="text-2xl font-bold text-red-600">{efficiency.scanCost}</div>
                                    <div className="text-sm text-gray-600">Custo Table Scan</div>
                                </div>
                                <div className="text-center p-4 bg-green-50 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">{efficiency.improvement}%</div>
                                    <div className="text-sm text-gray-600">Melhoria</div>
                                </div>
                            </div>

                            <div className="p-4 bg-gray-50 rounded-lg">
                                <div className="text-sm font-medium mb-2">Análise:</div>
                                <div className="text-sm text-gray-700">
                                    O índice hash reduziu o custo de busca
                                    em <strong>{efficiency.improvement}%</strong> comparado ao
                                    table scan sequencial.
                                    {efficiency.improvement > 80 && " Excelente performance!"}
                                    {efficiency.improvement > 50 && efficiency.improvement <= 80 && " Boa performance."}
                                    {efficiency.improvement <= 50 && " Performance pode ser melhorada ajustando parâmetros."}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
