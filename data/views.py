from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DataSerializer, CryptoSerializer
from .models import Crypto
from rest_framework.generics import ListAPIView
import yfinance as yf


# Create your views here.
class OhlcData(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = DataSerializer

    def post(self, request, *args, **kwargs):
        """
           A view that get data Financial market .

           Parameters:
                 name (string): currency name.
                 interval (string): currency interval.
                 period (string) : currency period.
        """
        try:
            name = self.request.data['name']
            try:
                interval = self.request.data['interval']
            except KeyError:
                interval = "1h"
            try:
                period = self.request.data['period']
            except KeyError:
                period = "24h"
            data = yf.download(tickers=f'{name}', period=f'{period}', interval=f'{interval}')
            result = data.to_json(orient="records")
        except:
            return Response("Enter your currency name .", status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK, data=result)


class CryptoList(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = CryptoSerializer
    queryset = Crypto.objects.all()
