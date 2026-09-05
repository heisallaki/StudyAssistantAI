import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from '../components/common/ProtectedRoute'
import AppLayout from '../layouts/AppLayout'
import ProgressAnalyticsPage from '../pages/analytics/ProgressAnalyticsPage'
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import DashboardPage from '../pages/dashboard/DashboardPage'
import DocumentDetailPage from '../pages/documents/DocumentDetailPage'
import DocumentsPage from '../pages/documents/DocumentsPage'
import DeckDetailPage from '../pages/flashcards/DeckDetailPage'
import DecksPage from '../pages/flashcards/DecksPage'
import FlashcardReviewPage from '../pages/flashcards/FlashcardReviewPage'
import PlannerPage from '../pages/planner/PlannerPage'
import ProfilePage from '../pages/profile/ProfilePage'
import QuizAttemptPage from '../pages/quizzes/QuizAttemptPage'
import QuizDetailPage from '../pages/quizzes/QuizDetailPage'
import QuizHistoryPage from '../pages/quizzes/QuizHistoryPage'
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
          <Route path="/quizzes/history" element={<QuizHistoryPage />} />
          <Route path="/quizzes/:quizId" element={<QuizDetailPage />} />
          <Route path="/quizzes/:quizId/attempts/:attemptId" element={<QuizAttemptPage />} />
          <Route path="/flashcards" element={<DecksPage />} />
          <Route path="/flashcards/:deckId" element={<DeckDetailPage />} />
          <Route path="/flashcards/:deckId/review" element={<FlashcardReviewPage />} />
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/analytics" element={<ProgressAnalyticsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default AppRoutes