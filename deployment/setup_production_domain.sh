#!/bin/bash
# Complete Production Domain Setup Guide
# Handles both LoadBalancer and Ingress with custom domains

set -e

echo "=========================================="
echo "🌐 Production Domain Setup Guide"
echo "=========================================="

echo "Choose your production setup method:"
echo ""
echo "1. LoadBalancer + Custom Domain (Simple)"
echo "   - Gets external IP/hostname"
echo "   - Point your domain to it via DNS"
echo "   - No SSL by default (HTTP only)"
echo ""
echo "2. Ingress + Custom Domain (Advanced)"
echo "   - Uses Application Load Balancer"
echo "   - Supports SSL certificates"
echo "   - More production features"
echo ""
echo "3. LoadBalancer + SSL Certificate (Recommended)"
echo "   - Simple setup with SSL support"
echo "   - Best of both worlds"
echo ""

read -p "Choose method (1/2/3): " method

case $method in
    1)
        echo ""
        echo "Setting up LoadBalancer + Custom Domain..."
        
        # Set up LoadBalancer
        kubectl patch svc chatbot-api -n chatbot -p '{"spec":{"type":"LoadBalancer"}}'
        
        echo "✅ LoadBalancer service created"
        echo ""
        echo "Waiting for external IP assignment..."
        kubectl get svc chatbot-api -n chatbot
        
        echo ""
        echo "=========================================="
        echo "🎉 LoadBalancer Setup Complete!"
        echo "=========================================="
        echo ""
        echo "Next steps for custom domain:"
        echo ""
        echo "1. Get LoadBalancer hostname/IP:"
        echo "   kubectl get svc chatbot-api -n chatbot"
        echo ""
        echo "2. Configure DNS:"
        echo "   - If you get an IP: Create A record"
        echo "   - If you get hostname: Create CNAME record"
        echo ""
        echo "3. Example DNS records:"
        echo "   A record: chatbot.yourdomain.com → <LOADBALANCER_IP>"
        echo "   CNAME: chatbot.yourdomain.com → <LOADBALANCER_HOSTNAME>"
        echo ""
        echo "4. Test your domain:"
        echo "   curl http://your-domain.com/health"
        echo ""
        ;;
        
    2)
        echo ""
        echo "Setting up Ingress + Custom Domain..."
        echo "This requires AWS Load Balancer Controller"
        echo ""
        
        read -p "Enter your domain (e.g., chatbot.yourdomain.com): " domain
        
        if [ -z "$domain" ]; then
            echo "❌ Domain is required. Exiting."
            exit 1
        fi
        
        # Create ingress with custom domain
        cat > kubernetes/ingress-production.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chatbot-ingress-production
  namespace: chatbot
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
spec:
  rules:
  - host: $domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: chatbot-api
            port:
              number: 80
EOF
        
        kubectl apply -f kubernetes/ingress-production.yaml
        
        echo "✅ Ingress created for $domain"
        echo ""
        echo "=========================================="
        echo "🎉 Ingress Setup Complete!"
        echo "=========================================="
        echo ""
        echo "Next steps:"
        echo ""
        echo "1. Get ALB hostname:"
        echo "   kubectl get ingress chatbot-ingress-production -n chatbot"
        echo ""
        echo "2. Configure DNS:"
        echo "   CNAME: $domain → <ALB_HOSTNAME>"
        echo ""
        echo "3. Test your domain:"
        echo "   curl http://$domain/health"
        echo ""
        ;;
        
    3)
        echo ""
        echo "Setting up LoadBalancer + SSL Certificate..."
        
        # Set up LoadBalancer
        kubectl patch svc chatbot-api -n chatbot -p '{"spec":{"type":"LoadBalancer"}}'
        
        echo "✅ LoadBalancer service created"
        echo ""
        echo "=========================================="
        echo "🎉 LoadBalancer + SSL Setup Complete!"
        echo "=========================================="
        echo ""
        echo "For SSL certificate setup:"
        echo ""
        echo "1. Get LoadBalancer hostname:"
        echo "   kubectl get svc chatbot-api -n chatbot"
        echo ""
        echo "2. Create SSL certificate in AWS Certificate Manager:"
        echo "   - Go to AWS Certificate Manager"
        echo "   - Request a public certificate"
        echo "   - Add your domain (e.g., chatbot.yourdomain.com)"
        echo "   - Validate domain ownership"
        echo ""
        echo "3. Configure DNS:"
        echo "   CNAME: your-domain.com → <LOADBALANCER_HOSTNAME>"
        echo ""
        echo "4. Update LoadBalancer with SSL:"
        echo "   - Go to EC2 → Load Balancers"
        echo "   - Find your LoadBalancer"
        echo "   - Add HTTPS listener with your certificate"
        echo ""
        echo "5. Test:"
        echo "   curl https://your-domain.com/health"
        echo ""
        ;;
        
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "📊 Monitoring Commands"
echo "=========================================="
echo "Check service: kubectl get svc -n chatbot"
echo "Check ingress: kubectl get ingress -n chatbot"
echo "View logs: kubectl logs -n chatbot -l app=chatbot-api -f"
echo ""
echo "=========================================="
echo "🚀 Production Ready!"
echo "=========================================="
