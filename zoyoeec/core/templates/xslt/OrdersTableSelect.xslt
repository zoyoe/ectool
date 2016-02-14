<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="//ebay:OrderArray">
 <table id='select_table' style="width:2000px;" class='table'>
   <thead style="display:none">
    <th>CNSGMT_ID</th>
    <th>CONSIGNMENT_NUMBER</th>
    <th>POST_RG_TO_ACCT</th>
    <th>CHRG_CODE</th>
    <th>MERCHANT_CNSGNEE_CODE</th>
    <th>CNSGNEE_NAME</th>
    <th>CNSGNEE_BUS_NAME</th>
    <th>CNSGNEE_ADDR_LINE1</th>
    <th>CNSGNEE_SUBURB</th>
    <th>CNSGNEE_STATE_CODE</th>
    <th>CNSGNEE_PCODE</th>
    <th>CNSGNEE_CNTRY_CODE</th>
    <th>CNSGNEE_PHONE_NBR</th>
    <th>IS_PHONE_PRNT_REQD</th>
    <th>CNSGNEE_FAX_NBR</th>
    <th>DELIVY_INSTRN</th>
    <th>IS_SIGNTR_REQD</th>
<!--
    <th>IS_PART_DELIVY</th>
    <th>U_CMNTS</th>
    <th>ADD_TO_ADDRESS_BOOK</th>
    <th>CTC_AMT</th>
    <th>XREF</th>
    <th>IS_REF_PRINT_REQD</th>
    <th>REF2</th>
    <th>IS_REF2_PRINT_REQD</th>
    <th>CHRG_BCK_ACCT</th>
    <th>IS_RECURRG_CNSGMT</th>
    <th>RTN_NAME</th>
-->
   </thead>
   <tbody>
 <xsl:for-each select="./ebay:Order"> 
   <tr>
   <td class="CNSGMT_ID">C</td><!-- CNSGMT_ID -->
   <td class="CONSIGNMENG_NUMBER"></td>
   <td class="POST_RG_TO_ACCT"></td><!-- POST_RG_TO_ACCT -->
   <td class="CHRG_CODE">7C55</td>
   <td class="MERCHANT_CNSGNEE_CODE"></td>
   <td class="CNBSGNEE_NAME"><xsl:value-of select="ebay:ShippingAddress/ebay:Name"/></td> <!-- CNBSGNEE_NAME -->
   <td class="CNSGNEE_BUS_NAME"></td>
   <td class="CNSGNEE_ADDR_LINE1"><xsl:value-of select="ebay:ShippingAddress/ebay:Street1"/></td>
   <td class="CNSGNEE_SUBURB"><xsl:value-of select="ebay:ShippingAddress/ebay:CityName"/></td>
   <td class="CNSGNEE_STATE_CODE"><xsl:value-of select="ebay:ShippingAddress/ebay:StateOrProvince"/></td>
   <td class="CNSGNEE_STATE_PCODE"><xsl:value-of select="ebay:ShippingAddress/ebay:PostalCode"/></td>
   <td class="CNSGNEE_CNTRY_CODE"><xsl:value-of select="ebay:ShippingAddress/ebay:Country"/></td>
   <td class="CNSGNEE_PHONE_NBR"><xsl:value-of select="ebay:ShippingAddress/ebay:Phone"/></td>
   <td class="IS_PHONE_PRNT_REQD"></td><!-- RD-->
   <td class="CNSGNEE_FAX_NBR"></td><!-- RD--> 
   <td class="DELIVY_INSTRN"><xsl:value-of select="ebay:OrderID"/>
     <xsl:for-each select="./ebay:TransactionArray/ebay:Transaction"> 
       ;<xsl:value-of select="ebay:Item/ebay:SKU"/>
       [<xsl:value-of select="ebay:Item/ebay:Title"/>]<xsl:value-of select="ebay:Item/ebay:ItemID"/> * <xsl:value-of select="ebay:QuantityPurchased"/>
     </xsl:for-each>
   </td>
   <td class="IS_SIGNTR_REQD">True</td>
<!--
   <td class="IS_PART_DELIVY" ></td>
   <td class="U_CMNTS"></td>
   <td class="ADD_TO_ADDRESS_BOOK"></td>
   <td class="CTC_AMT" ></td>
   <td class="XREF"></td>
   <td class="IS_REF_PRINT_REQD"></td>
   <td class="REF2" ></td>
   <td class="IS_REF2_PRINT_REQD"></td>
   <td class="CHRG_BCK_ACCT"></td>
   <td class="IS_RECURRG_CNSGMT"></td>
   <td class="RTN_NAME"></td>
-->
   </tr>
 </xsl:for-each>
   </tbody>
 </table>
</xsl:template>
</xsl:stylesheet>
