import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {Alert, AlertDescription } from "./ui/alert"

interface TableScanVisualizationProps {
  records: Array<{
    index: number
    value: string
    page: number
    found?: boolean
  }>
  isScanning: boolean
  totalScanned?: number
  limitedView?: boolean
}

export function TableScanVisualization({
  records,
  isScanning,
  totalScanned = 0,
  limitedView = false
}: TableScanVisualizationProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isScanning ? "bg-yellow-500 animate-pulse" : "bg-gray-400"}`}></div>
          Progresso do Table Scan
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Informações do scan */}
          {totalScanned > 0 && (
            <div className="flex gap-2 mb-4">
              <Badge variant="outline">
                Total Escaneado: {totalScanned.toLocaleString()}
              </Badge>
              <Badge variant="outline">
                Exibindo: {records.length}
              </Badge>
            </div>
          )}

          {/* Alerta se visualização limitada */}
          {limitedView && (
            <Alert className="mb-4">
              <AlertDescription>
                Exibindo apenas os primeiros {records.length} registros de {totalScanned.toLocaleString()} escaneados para melhor performance.
              </AlertDescription>
            </Alert>
          )}

          {records.length === 0 && !isScanning && (
            <div className="text-gray-500 text-center py-8">
              Nenhum scan executado ainda. Digite uma palavra e clique em "Iniciar Table Scan".
            </div>
          )}

          {/* Lista de registros com scroll */}
          <div className="max-h-96 overflow-y-auto space-y-2">
            {records.map((record, index) => (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-lg ${
                  record.found 
                    ? "bg-green-100 border border-green-300" 
                    : "bg-gray-50"
                }`}
              >
                <Badge variant="outline" className="min-w-fit">
                  {record.index}
                </Badge>
                <Badge variant="secondary" className="min-w-fit">
                  P{record.page}
                </Badge>
                <span className="font-mono text-sm flex-1 truncate">
                  {record.value}
                </span>
                {record.found && (
                  <Badge variant="default" className="bg-green-600">
                    ENCONTRADO
                  </Badge>
                )}
              </div>
            ))}
          </div>

          {isScanning && (
            <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-yellow-800">Escaneando páginas...</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}