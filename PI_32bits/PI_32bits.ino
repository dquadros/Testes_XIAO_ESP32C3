/*
 * Calculo dos dígito de Pi
 * Usando o algoritimo Spigot de Rabinowitz e Wagon
 * Adaptação da versão compacta e obsfucada escrita por Dik T. Winter:
 * 
 * int a=10000,b,c=2800,d,e,f[2801],g;main(){for(;b-c;)f[b++]=a/5;
 * for(;d=0,g=c*2;c-=14,printf("%.4d",e+d/a),e=d%a)for(b=c;d+=f[b]*a,
 * f[b]=d%--g,d/=g--,--b;d*=b);}
 * 
 * Comentários nas declarações copiados de
 * https://stackoverflow.com/questions/4084571/implementing-the-spigot-algorithm-for-%CF%80-pi
 * 
 * Daniel Quadros junho/2021
 */
 
#define NDIGITS 2000           //max digits to compute
#define LEN (NDIGITS/4+1)*14   //nec. array length
 
int32_t a = 10000;             //new base, 4 decimal digits
int32_t b = 0;                 //nominator prev. base
int32_t c = LEN;               //index
int32_t d = 0;                 //accumulator and carry
int32_t e = 0;                 //save previous 4 digits
int32_t f[LEN+1];              //array of 4-digit-decimals
int32_t g = 0;                 //denom previous base

// Iniciação
void setup() {
  delay(1000);
  Serial.begin(115200);
}

// Programa principal
void loop() {
  while (Serial.read() != '\n') {
    delay(100); 
  }
  Serial.print("CPU freq = ");
  Serial.print(getCpuFrequencyMhz());
  Serial.println(" MHz");
  Serial.println("PI = ");
  long inicio = millis();
  calcula();
  long tempo = millis() - inicio;
  Serial.println();
  Serial.print ("Tempo = ");
  Serial.print (tempo);
  Serial.println ("ms");
}

// Cálculo dos dígitos do Pi
void calcula() {
  char dig[5] = "0000"; // para fazer o print
  int n = 0;            // para mudar de linha a cada 100 dígitos

  c = LEN;
  for(b = 0; b < c; b++) {
    f[b] = a/5;
  }

  e = 0;
  for (; c > 0; c -= 14) {
      d = 0;
      g = c*2;
      b = c;
      for (;;) {
          d += f[b]*a;
          f[b] = d % --g;
          d /= g--;
          if (--b == 0) {
              break;
          }
          d *= b;
      }
      uint16_t val = e+d/a;
      dig[0] = (val / 1000) + '0'; 
      dig[1] = ((val / 100) % 10) + '0'; 
      dig[2] = ((val / 10) % 10) + '0'; 
      dig[3] = (val % 10) + '0'; 
      Serial.print (dig);
      n += 4;
      if (n == 100) {
        Serial.println();
        n = 0;
      }
      e = d % a;
  }
}
