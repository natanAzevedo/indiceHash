"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { HashVisualization } from "@/components/hash-visualization"
import { TableScanVisualization } from "@/components/table-scan-visualization"
import { StatisticsPanel } from "@/components/statistics-panel"
import { SearchResults } from "@/components/search-results"

const API_BASE = "http://127.0.0.1:5000"

interface TableData {
  total_tuplas: number
  total_paginas: number
}

interface Statistics {
  total_buckets: number
  total_registros: number
  taxa_colisoes: number
  taxa_overflows: number
  fator_carga: number
}

interface SearchResult {
  tempo_busca: string
  encontrado: boolean
  resultado: any
  pagina_id?: number
  custo: number
  scanned_records?: string[]  // Novo campo para registros escaneados
}

export default function HashIndexInterface() {
  const [tableData, setTableData] = useState<TableData | null>(null)
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [searchKey, setSearchKey] = useState("")
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null)
  const [scanResult, setScanResult] = useState<SearchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [pageSize, setPageSize] = useState(100)
  const [bucketSize, setBucketSize] = useState(50)
  const [isIndexBuilt, setIsIndexBuilt] = useState(false)
  const [scanProgress, setScanProgress] = useState(0)
  const [scanRecords, setScanRecords] = useState<string[]>([])

  const handleLoadData = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch(`${API_BASE}/load_data`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tamanho_pagina: pageSize }),
      })

      if (response.ok) {
        const data = await response.json()
        setTableData(data)
      } else {
        const errorData = await response.json()
        setError(errorData.erro || "Erro ao carregar dados")
      }
    } catch (err) {
      setError("Erro de conexão com a API")
    }
    setLoading(false)
  }

  const handleBuildIndex = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch(`${API_BASE}/build_index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tamanho_bucket_fr: bucketSize }),
      })

      if (response.ok) {
        setIsIndexBuilt(true)
        await loadStatistics()
      } else {
        const errorData = await response.json()
        setError(errorData.erro || "Erro ao construir índice")
      }
    } catch (err) {
      setError("Erro de conexão com a API")
    }
    setLoading(false)
  }

  const loadStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/statistics`)
      if (response.ok) {
        const data = await response.json()
        setStatistics(data)
      }
    } catch (err) {
      console.error("Erro ao carregar estatísticas:", err)
    }
  }

  useEffect(() => {
    if (isIndexBuilt) {
      loadStatistics()
    }
  }, [isIndexBuilt])

  const handleHashSearch = async () => {
    if (!searchKey.trim()) return

    setLoading(true)
    setError("")
    try {
      const response = await fetch(`${API_BASE}/search_hash/${encodeURIComponent(searchKey)}`)
      if (response.ok) {
        const data = await response.json()
        setSearchResult(data)
      } else {
        const errorData = await response.json()
        setError(errorData.erro || "Erro na busca")
      }
    } catch (err) {
      setError("Erro de conexão com a API")
    }
    setLoading(false)
  }

  const handleTableScan = async () => {
    if (!searchKey.trim()) return

    setLoading(true)
    setError("")
    setScanProgress(0)
    setScanRecords([])

    try {
      const response = await fetch(`${API_BASE}/search_scan/${encodeURIComponent(searchKey)}`)
      if (response.ok) {
        const data = await response.json()
        setScanResult(data)
        setScanRecords(data.scanned_records || [])  // Usa registros reais do backend
        setScanProgress(100)
      } else {
        const errorData = await response.json()
        setError(errorData.erro || "Erro no table scan")
      }
    } catch (err) {
      setError("Erro de conexão com a API")
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Sistema de Índice Hash</h1>
          <p className="text-lg text-gray-600">
            Interface para demonstração de estruturas de dados e algoritmos de busca
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {/* Configuration Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              Configuração do Sistema
            </CardTitle>
            <CardDescription>Configure os parâmetros antes de carregar os dados</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="pageSize">Tamanho da Página</Label>
                <Input
                  id="pageSize"
                  type="number"
                  value={pageSize}
                  onChange={(e) => setPageSize(Number(e.target.value))}
                  disabled={tableData !== null}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bucketSize">Tamanho do Bucket (FR)</Label>
                <Input
                  id="bucketSize"
                  type="number"
                  value={bucketSize}
                  onChange={(e) => setBucketSize(Number(e.target.value))}
                  disabled={isIndexBuilt}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={handleLoadData} disabled={loading || tableData !== null} className="w-full">
                  {loading ? "Carregando..." : "Carregar Dados"}
                </Button>
              </div>
            </div>

            {tableData && (
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-4">
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    {tableData.total_tuplas.toLocaleString()} tuplas carregadas
                  </Badge>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    {tableData.total_paginas} páginas criadas
                  </Badge>
                </div>
                <Button
                  onClick={handleBuildIndex}
                  disabled={loading || isIndexBuilt}
                  variant={isIndexBuilt ? "secondary" : "default"}
                >
                  {isIndexBuilt ? "Índice Construído" : "Construir Índice Hash"}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Main Interface */}
        {tableData && (
          <Tabs defaultValue="visualization" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="visualization">Visualização</TabsTrigger>
              <TabsTrigger value="search">Busca</TabsTrigger>
              <TabsTrigger value="scan">Table Scan</TabsTrigger>
              <TabsTrigger value="statistics">Estatísticas</TabsTrigger>
            </TabsList>

            <TabsContent value="visualization" className="space-y-6">
              <HashVisualization tableData={tableData} statistics={statistics} isIndexBuilt={isIndexBuilt} />
            </TabsContent>

            <TabsContent value="search" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Busca por Índice Hash</CardTitle>
                  <CardDescription>Digite uma palavra para buscar usando o índice hash</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Digite a palavra para buscar..."
                      value={searchKey}
                      onChange={(e) => setSearchKey(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleHashSearch()}
                    />
                    <Button onClick={handleHashSearch} disabled={!isIndexBuilt || loading || !searchKey.trim()}>
                      Buscar
                    </Button>
                  </div>

                  {searchResult && <SearchResults result={searchResult} type="hash" searchKey={searchKey} />}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="scan" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Table Scan Sequencial</CardTitle>
                  <CardDescription>Busca sequencial percorrendo todas as páginas</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Digite a palavra para buscar..."
                      value={searchKey}
                      onChange={(e) => setSearchKey(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleTableScan()}
                    />
                    <Button onClick={handleTableScan} disabled={loading || !searchKey.trim()}>
                      Iniciar Table Scan
                    </Button>
                  </div>

                  {loading && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Progresso do Scan</span>
                        <span>Carregando...</span>
                      </div>
                      <Progress value={undefined} className="w-full" /> {/* Indicador de loading indeterminado */}
                    </div>
                  )}

                  <TableScanVisualization records={scanRecords} isScanning={loading} />

                  {scanResult && <SearchResults result={scanResult} type="scan" searchKey={searchKey} />}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="statistics" className="space-y-6">
              <StatisticsPanel
                statistics={statistics}
                tableData={tableData}
                searchResult={searchResult}
                scanResult={scanResult}
              />
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  )
}
