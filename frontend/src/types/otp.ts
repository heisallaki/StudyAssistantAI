export interface MessageResponse {
  message: string
}

export interface EmailVerificationRequest {
  email: string
  code: string
}

export interface OtpRequestByEmail {
  email: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
  code: string
}

export interface AccountDeletionRequest {
  code: string
}