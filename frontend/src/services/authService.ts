import { authAPI } from './api'

export async function loginUser(
  email: string,
  password: string
) {
  const response = await authAPI.login(
    email,
    password
  )

  return response.data
}