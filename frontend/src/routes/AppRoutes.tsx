import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from '../components/common/ProtectedRoute'
import AppLayout from '../layouts/AppLayout'
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import DashboardPage from '../pages/dashboard/DashboardPage'
import DocumentDetailPage from '../pages/documents/DocumentDetailPage'
import DocumentsPage from '../pages/documents/DocumentsPage'
import ProfilePage from '../pages/profile/ProfilePage'
import QuizDetailPage from '../pages/quizzes/QuizDetailPage'
import QuizzesPage from '../pages/quizzes/QuizzesPage'
import SubjectDetailPage from '../pages/subjects/SubjectDetailPage'
import SubjectsListPage from '../pages/subjects/SubjectsListPage'
import ChatPage from '../pages/tutor/ChatPage'
import ConversationsPage from '../pages/tutor/ConversationsPage'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/subjects" element={<SubjectsListPage />} />
          <Route path="/subjects/:subjectId" element={<SubjectDetailPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
          <Route path="/tutor" element={<ConversationsPage />} />
          <Route path="/tutor/:conversationId" element={<ChatPage />} />
          <Route path="/quizzes" element={<QuizzesPage />} />
          <Route path="/quizzes/:quizId" element={<QuizDetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default AppRoutes