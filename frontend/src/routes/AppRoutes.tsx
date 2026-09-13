import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import AdminRoute from '../components/common/AdminRoute'
import ProtectedRoute from '../components/common/ProtectedRoute'
import AppLayout from '../layouts/AppLayout'
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import DashboardPage from '../pages/dashboard/DashboardPage'

const AdminAuditLogPage = lazy(() => import('../pages/admin/AdminAuditLogPage'))
const AdminDashboardPage = lazy(() => import('../pages/admin/AdminDashboardPage'))
const AdminUsersPage = lazy(() => import('../pages/admin/AdminUsersPage'))
const ProgressAnalyticsPage = lazy(() => import('../pages/analytics/ProgressAnalyticsPage'))
const DocumentDetailPage = lazy(() => import('../pages/documents/DocumentDetailPage'))
const DocumentsPage = lazy(() => import('../pages/documents/DocumentsPage'))
const DeckDetailPage = lazy(() => import('../pages/flashcards/DeckDetailPage'))
const DecksPage = lazy(() => import('../pages/flashcards/DecksPage'))
const FlashcardReviewPage = lazy(() => import('../pages/flashcards/FlashcardReviewPage'))
const NotificationsPage = lazy(() => import('../pages/notifications/NotificationsPage'))
const PlannerPage = lazy(() => import('../pages/planner/PlannerPage'))
const ProfilePage = lazy(() => import('../pages/profile/ProfilePage'))
const QuizAttemptPage = lazy(() => import('../pages/quizzes/QuizAttemptPage'))
const QuizDetailPage = lazy(() => import('../pages/quizzes/QuizDetailPage'))
const QuizHistoryPage = lazy(() => import('../pages/quizzes/QuizHistoryPage'))
const QuizzesPage = lazy(() => import('../pages/quizzes/QuizzesPage'))
const SearchPage = lazy(() => import('../pages/search/SearchPage'))
const SubjectDetailPage = lazy(() => import('../pages/subjects/SubjectDetailPage'))
const SubjectsListPage = lazy(() => import('../pages/subjects/SubjectsListPage'))
const ChatPage = lazy(() => import('../pages/tutor/ChatPage'))
const ConversationsPage = lazy(() => import('../pages/tutor/ConversationsPage'))

function RouteLoadingFallback() {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <CircularProgress />
    </Box>
  )
}

function AppRoutes() {
  return (
    <Suspense fallback={<RouteLoadingFallback />}>
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
            <Route path="/quizzes/history" element={<QuizHistoryPage />} />
            <Route path="/quizzes/:quizId" element={<QuizDetailPage />} />
            <Route path="/quizzes/:quizId/attempts/:attemptId" element={<QuizAttemptPage />} />
            <Route path="/flashcards" element={<DecksPage />} />
            <Route path="/flashcards/:deckId" element={<DeckDetailPage />} />
            <Route path="/flashcards/:deckId/review" element={<FlashcardReviewPage />} />
            <Route path="/planner" element={<PlannerPage />} />
            <Route path="/analytics" element={<ProgressAnalyticsPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminDashboardPage />} />
              <Route path="/admin/users" element={<AdminUsersPage />} />
              <Route path="/admin/audit-log" element={<AdminAuditLogPage />} />
            </Route>
          </Route>
        </Route>
      </Routes>
    </Suspense>
  )
}

export default AppRoutes