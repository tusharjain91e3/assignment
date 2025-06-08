import { NextRequest, NextResponse } from 'next/server';
import { jwtVerify } from 'jose';

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET || 'your-secret-key');
const API_PREFIX = '/api';

// Rate limiting store (in production, use Redis)
const rateLimitStore = new Map<string, { count: number; timestamp: number }>();

// Rate limiting configuration
const RATE_LIMIT = {
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxRequests: 100, // per window
};

interface BackendResponse {
  data?: any;
  error?: string;
  status: number;
}

class APIError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

// Rate limiting function
function checkRateLimit(identifier: string): boolean {
  const now = Date.now();
  const userRecord = rateLimitStore.get(identifier);
  
  if (!userRecord || now - userRecord.timestamp > RATE_LIMIT.windowMs) {
    rateLimitStore.set(identifier, { count: 1, timestamp: now });
    return true;
  }
  
  if (userRecord.count >= RATE_LIMIT.maxRequests) {
    return false;
  }
  
  userRecord.count++;
  return true;
}

// JWT verification function
async function verifyToken(token: string): Promise<any> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload;
  } catch (error) {
    throw new APIError('Invalid token', 401);
  }
}

// Backend API caller
async function callBackendAPI(
  endpoint: string,
  method: string = 'GET',
  body?: any,
  headers?: Record<string, string>
): Promise<BackendResponse> {
  try {
    const url = `${BACKEND_URL}${endpoint}`;
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...headers,
    };

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      ...(body && { body: JSON.stringify(body) }),
    };

    console.log(`[API Call] ${method} ${url}`);
    
    const response = await fetch(url, requestOptions);
    
    let data;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      console.error(`[API Error] ${response.status}: ${JSON.stringify(data)}`);
      return {
        error: data.detail || data.message || 'Backend error',
        status: response.status,
      };
    }

    return { data, status: response.status };
  } catch (error) {
    console.error('[Backend Connection Error]:', error);
    return {
      error: 'Failed to connect to backend service',
      status: 500,
    };
  }
}

// Main middleware function
export async function middleware(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl;
  
  // Skip middleware for non-API routes
  if (!pathname.startsWith(API_PREFIX)) {
    return NextResponse.next();
  }

  // Get client identifier for rate limiting
  const clientIP = request.ip || request.headers.get('x-forwarded-for') || 'unknown';
  const userAgent = request.headers.get('user-agent') || '';
  const identifier = `${clientIP}-${userAgent}`;

  try {
    // Apply rate limiting
    if (!checkRateLimit(identifier)) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Please try again later.' },
        { status: 429 }
      );
    }

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new NextResponse(null, {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // Extract route and prepare backend endpoint
    const apiRoute = pathname.replace(API_PREFIX, '');
    let backendEndpoint = apiRoute;
    
    // Map frontend routes to backend routes if needed
    const routeMapping: Record<string, string> = {
      '/chat': '/chat',
      '/products': '/products',
      '/orders': '/orders',
      '/auth/login': '/auth/login',
      '/auth/register': '/auth/register',
      '/user/profile': '/user/profile',
    };

    if (routeMapping[apiRoute]) {
      backendEndpoint = routeMapping[apiRoute];
    }

    // Handle authentication for protected routes
    const protectedRoutes = ['/chat', '/orders', '/user/profile'];
    let authHeaders: Record<string, string> = {};

    if (protectedRoutes.some(route => apiRoute.startsWith(route))) {
      const authHeader = request.headers.get('authorization');
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return NextResponse.json(
          { error: 'Authentication required' },
          { status: 401 }
        );
      }

      const token = authHeader.substring(7);
      
      try {
        const payload = await verifyToken(token);
        authHeaders['Authorization'] = authHeader;
        authHeaders['X-User-ID'] = payload.user_id?.toString() || '';
      } catch (error) {
        return NextResponse.json(
          { error: 'Invalid authentication token' },
          { status: 401 }
        );
      }
    }

    // Prepare request body
    let requestBody;
    if (request.method !== 'GET' && request.method !== 'DELETE') {
      try {
        requestBody = await request.json();
      } catch (error) {
        // Handle cases where body is not JSON or empty
        requestBody = null;
      }
    }

    // Add query parameters to endpoint
    if (searchParams.toString()) {
      backendEndpoint += `?${searchParams.toString()}`;
    }

    // Call backend API
    const backendResponse = await callBackendAPI(
      backendEndpoint,
      request.method,
      requestBody,
      authHeaders
    );

    // Handle backend response
    if (backendResponse.error) {
      return NextResponse.json(
        { error: backendResponse.error },
        { status: backendResponse.status }
      );
    }

    // Return successful response with CORS headers
    return NextResponse.json(backendResponse.data, {
      status: backendResponse.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });

  } catch (error) {
    console.error('[Middleware Error]:', error);
    
    if (error instanceof APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.status }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    '/api/:path*',
  ],
};

// Utility functions for frontend components
export const apiClient = {
  // Chat-related API calls
  async sendMessage(message: string, conversationId?: string) {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    return response.json();
  },

  // Product search
  async searchProducts(query: string, filters?: any) {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`/api/products/search?${params}`);
    return response.json();
  },

  // Get product details
  async getProduct(productId: string) {
    const response = await fetch(`/api/products/${productId}`);
    return response.json();
  },

  // User authentication
  async login(email: string, password: string) {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  },

  // Get user orders
  async getOrders() {
    const response = await fetch('/api/orders', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });
    return response.json();
  },

  // Get user profile
  async getUserProfile() {
    const response = await fetch('/api/user/profile', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    });
    return response.json();
  },
};