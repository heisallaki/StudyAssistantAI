export type AcademicLevel = 'high_school' | 'undergraduate' | 'graduate' | 'postgraduate' | 'other'

export interface Profile {
  id: string
  user_id: string
  full_name: string | null
  academic_level: AcademicLevel | null
  institution: string | null
  program: string | null
  subjects: string[]
  academic_goals: string | null
  created_at: string
  updated_at: string
}

export interface ProfileUpdateRequest {
  full_name?: string | null
  academic_level?: AcademicLevel | null
  institution?: string | null
  program?: string | null
  subjects?: string[]
  academic_goals?: string | null
}