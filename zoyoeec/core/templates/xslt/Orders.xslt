<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="//ebay:OrderArray">
 <div class="col-lg-3 col-md-4 col-sm-6">
 <xsl:for-each select="./ebay:Order"> 
   <div class="panel panel-default">
   <div class="panel-heading"><h6 class="panel-title">
    order id:<xsl:value-of select="ebay:OrderID"/></h6></div>
   <div class="panel-body">
    <ul>
    <li>amount paid:<xsl:value-of select="ebay:AmountPaid"/></li>
    <li>name:<xsl:value-of select="ebay:ShippingAddress/ebay:Name"/></li>
    <li>address:<xsl:value-of select="ebay:ShippingAddress/ebay:Street1"/></li>
    <li>city:<xsl:value-of select="ebay:ShippingAddress/ebay:CityName"/></li>
    <li>state:<xsl:value-of select="ebay:ShippingAddress/ebay:StateOrProvince"/></li>
    <li>country:<xsl:value-of select="ebay:ShippingAddress/ebay:Country"/></li>
    <li>postalcode:<xsl:value-of select="ebay:ShippingAddress/ebay:PostalCode"/></li>
    <xsl:for-each select="./ebay:TransactionArray"> 
      <li>buyer:<xsl:value-of select="ebay:Transaction/ebay:Buyer/ebay:Email"/></li>
    </xsl:for-each>
    </ul>
   </div>
   </div>
 </xsl:for-each>
 </div>
</xsl:template>
</xsl:stylesheet>
