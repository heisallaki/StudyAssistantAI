import { useEffect } from 'react'
import { matchPath, useLocation } from 'react-router-dom'
import { OG_IMAGE_PATH, SITE_DESCRIPTION, SITE_NAME, SITE_URL } from '../../config/site'

interface RouteMeta {
  title: string
  description: string
  indexable: boolean
}

interface RouteRule {
  path: string
  meta: RouteMeta
}

const INDEXABLE_ROBOTS = 'index, follow, max-image-preview:large'
const PRIVATE_ROBOTS = 'noindex, nofollow'

function privateMeta(title: string): RouteMeta {
  return { title: `${title} | ${SITE_NAME}`, description: SITE_DESCRIPTION, indexable: false }
}

const ROUTE_RULES: RouteRule[] = [
  {
    path: '/login',
    meta: {
      title: `${SITE_NAME}: sign in to your AI study tutor`,
      description: SITE_DESCRIPTION,
      indexable: true,
    },
  },
  {
    path: '/register',
    meta: {
      title: `Create your account | ${SITE_NAME}`,
      description:
        'Create a StudyAssistant AI account to upload your notes, chat with an AI tutor, and turn your material into quizzes and flashcards.',
      indexable: true,
    },
  },
  {
    path: '/privacy',
    meta: {
      title: `Privacy Policy | ${SITE_NAME}`,
      description:
        'What StudyAssistant AI collects, which services your notes and chats pass through, and how to delete your data.',
      indexable: true,
    },
  },
  {
    path: '/terms',
    meta: {
      title: `Terms of Use | ${SITE_NAME}`,
      description: 'The short, plain-language rules for using StudyAssistant AI.',
      indexable: true,
    },
  },
  {
    path: '/disclaimer',
    meta: {
      title: `AI Disclaimer | ${SITE_NAME}`,
      description:
        'AI answers, quizzes and study plans can be wrong. Read how to use StudyAssistant AI responsibly.',
      indexable: true,
    },
  },
  { path: '/verify-email', meta: privateMeta('Verify your email') },
  { path: '/forgot-password', meta: privateMeta('Reset your password') },
  { path: '/', meta: privateMeta('Dashboard') },
  { path: '/subjects/*', meta: privateMeta('Subjects') },
  { path: '/documents/*', meta: privateMeta('Documents') },
  { path: '/tutor/*', meta: privateMeta('AI Tutor') },
  { path: '/quizzes/*', meta: privateMeta('Quizzes') },
  { path: '/flashcards/*', meta: privateMeta('Flashcards') },
  { path: '/planner', meta: privateMeta('Planner') },
  { path: '/analytics', meta: privateMeta('Analytics') },
  { path: '/notifications', meta: privateMeta('Notifications') },
  { path: '/search', meta: privateMeta('Search') },
  { path: '/profile', meta: privateMeta('Profile') },
  { path: '/admin/*', meta: privateMeta('Admin') },
]

const FALLBACK_META: RouteMeta = privateMeta('Page not found')

function resolveRouteMeta(pathname: string): RouteMeta {
  const rule = ROUTE_RULES.find((candidate) => matchPath({ path: candidate.path, end: true }, pathname))
  return rule ? rule.meta : FALLBACK_META
}

function setMeta(attribute: 'name' | 'property', key: string, content: string) {
  let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, key)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

function setCanonical(href: string | null) {
  let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (href === null) {
    link?.remove()
    return
  }
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', href)
}

function RouteSeo() {
  const { pathname } = useLocation()

  useEffect(() => {
    const meta = resolveRouteMeta(pathname)
    const normalizedPath = pathname.replace(/\/+$/, '') || '/'
    const url = `${SITE_URL}${normalizedPath === '/' ? '/' : normalizedPath}`

    document.title = meta.title
    setMeta('name', 'description', meta.description)
    setMeta('name', 'robots', meta.indexable ? INDEXABLE_ROBOTS : PRIVATE_ROBOTS)
    setCanonical(meta.indexable ? url : null)
    setMeta('property', 'og:title', meta.title)
    setMeta('property', 'og:description', meta.description)
    setMeta('property', 'og:url', url)
    setMeta('property', 'og:image', `${SITE_URL}${OG_IMAGE_PATH}`)
    setMeta('name', 'twitter:title', meta.title)
    setMeta('name', 'twitter:description', meta.description)
  }, [pathname])

  return null
}

export default RouteSeo