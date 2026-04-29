import request from '@/utils/request'

export const executeCompareApi = (env: string) => {
  if (env === 'ALL') {
    return request.post('/api/dbcompare/all')
  }
  return request.post(`/api/dbcompare/${env.toLowerCase()}`)
}

export const executeSingleCompareApi = (env: string, db: string) => {
  return request.post(`/api/dbcompare/${env}/${db}`)
}

export const getRecordListApi = (params: { pageNum: number; pageSize: number }) => {
  return request.get('/api/dbcompare/records', { params })
}

export const getScheduleConfigApi = () => {
  return request.get('/api/dbcompare/schedule')
}

export const updateScheduleConfigApi = (data: any) => {
  return request.post('/api/dbcompare/schedule', data)
}
